# window.py
#
# Copyright 2024 logonoff <hello@logonoff.co>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
from concurrent.futures import ThreadPoolExecutor
from gi.repository import Adw
from gi.repository import GLib
from gi.repository import Gtk
from .add_dialog import AddDialogBox
from .settings_manager import SettingsManager
from .wol_client import WolClient

@Gtk.Template(resource_path='/co/logonoff/awakeonlan/window.ui')
class awakeonlanWindow(Adw.ApplicationWindow):
    """Main application window."""
    __gtype_name__ = 'awakeonlanWindow'

    # How often the online status of the remotes is refreshed, in seconds
    STATUS_INTERVAL = 5
    # How long to wait for a single ICMP reply, in seconds
    STATUS_TIMEOUT = 1.0
    # Possible states of the status dot
    STATUS_STATES = ('online', 'offline', 'checking', 'unknown')

    add_button: Gtk.Button = Gtk.Template.Child()
    remotes_list: Gtk.ListBox = Gtk.Template.Child()
    no_items: Adw.StatusPage = Gtk.Template.Child()
    toaster: Adw.ToastOverlay = Gtk.Template.Child()
    content_box: Gtk.Box = Gtk.Template.Child()
    wol_clients: SettingsManager

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title(_('Awake on LAN'))

        if sys.platform == 'win32':
            config_home = os.getenv('APPDATA', os.path.expanduser('~'))
        else:
            config_home = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))

        self.wol_clients = SettingsManager(base_path=config_home, version=self.get_application().version)
        self.wol_clients.load_settings()

        self._executor = ThreadPoolExecutor(
            max_workers=4, thread_name_prefix='awakeonlan-status'
        )
        self._status_timeout_id = 0
        self._pending_checks = set()

        self.get_application().create_action(
            'add', lambda *_: self.spawn_add_remote_dialog(None), ['<primary>n']
        )

        # self.get_application().create_action(
            # 'view-config', lambda *_: os.system(f'xdg-open {self.wol_clients.settings_file}'), ['<primary>m']
        # )

        for client in self.wol_clients.wol_clients:
            self._add_wol_client_to_list(client)

        self._show_no_items(not self.wol_clients.wol_clients)

        self._refresh_status()
        self._start_status_timer()
        self.connect('close-request', self._on_close_request)


    def _start_status_timer(self):
        """Start or restart the periodic status refresh."""
        if self._status_timeout_id:
            GLib.source_remove(self._status_timeout_id)
        self._status_timeout_id = GLib.timeout_add_seconds(
            self.STATUS_INTERVAL, self._refresh_status
        )


    def _on_close_request(self, _window) -> bool:
        """Stop the status polling when the window is closed."""
        if self._status_timeout_id:
            GLib.source_remove(self._status_timeout_id)
            self._status_timeout_id = 0
        self._executor.shutdown(wait=False, cancel_futures=True)
        return False


    def _refresh_status(self) -> bool:
        """Check the online status of all remotes in the background."""
        row = self.remotes_list.get_first_child()
        while row is not None:
            client = getattr(row, '_wol_client', None)
            dot = getattr(row, '_status_dot', None)
            if (client is not None and dot is not None and client.hostname
                    and dot not in self._pending_checks):
                self._pending_checks.add(dot)
                self._executor.submit(self._check_status, client, dot)
            row = row.get_next_sibling()
        return GLib.SOURCE_CONTINUE


    def _check_status(self, client, dot):
        """Probe a single remote; runs in a worker thread."""
        online = False
        try:
            online = client.is_online(timeout=self.STATUS_TIMEOUT)
        finally:
            self._pending_checks.discard(dot)
        GLib.idle_add(self._set_status, dot, online)


    def _set_status(self, dot, online: bool) -> bool:
        """Update the status dot of a remote; runs on the main loop."""
        if dot.get_root() is None:
            return GLib.SOURCE_REMOVE
        self._set_dot_state(dot, 'online' if online else 'offline')
        return GLib.SOURCE_REMOVE


    def _set_dot_state(self, dot, state: str):
        """Set the state of a status dot: online, offline, checking or unknown."""
        context = dot.get_style_context()
        for name in self.STATUS_STATES:
            context.remove_class(name)
        context.add_class(state)
        if state == 'online':
            dot.set_tooltip_text(_('Online'))
        elif state == 'offline':
            dot.set_tooltip_text(_('Offline'))
        elif state == 'checking':
            dot.set_tooltip_text(_('Checking...'))
        else:
            dot.set_tooltip_text(_('Status not available: no hostname set'))


    def _reset_status_dot(self, row):
        """Reset the status dot of a row after its hostname changed."""
        client = row._wol_client
        self._set_dot_state(
            row._status_dot, 'checking' if client.hostname else 'unknown'
        )
        self._refresh_status()


    def _show_no_items(self, show: bool):
        """Show or hide the no items page."""
        if show:
            self.no_items.show()
            self.content_box.hide()
        else:
            self.no_items.hide()
            self.content_box.show()


    def _add_wol_client_to_list(self, wol_client):
        """Add a new WolClient to the list and update the view."""
        self._show_no_items(False)

        new_row = Adw.ActionRow.new()
        new_row.set_title(wol_client.name)
        new_row.set_subtitle(wol_client.get_subtitle())
        new_row.get_style_context().add_class('AdwActionRow')
        new_row.set_activatable(True)
        new_row._wol_client = wol_client

        # online status indicator, only meaningful with a hostname to ping
        status_dot = Gtk.Box()
        status_dot.set_valign(Gtk.Align.CENTER)
        status_dot.get_style_context().add_class('status-dot')
        self._set_dot_state(
            status_dot, 'checking' if wol_client.hostname else 'unknown'
        )
        new_row.add_prefix(status_dot)
        new_row._status_dot = status_dot

        # kebab button (edit)
        kebab_button = Gtk.Button.new_from_icon_name('view-more')
        kebab_button.set_tooltip_text(_('Edit'))
        kebab_button.get_style_context().add_class('flat')

        kebab_button.connect('clicked', lambda _: self.spawn_edit_remote_dialog(wol_client, new_row))

        new_row.set_activatable_widget(kebab_button)
        new_row.add_suffix(kebab_button)

        # create start button
        start_button = Gtk.Button.new_from_icon_name('media-playback-start-symbolic')
        start_button.set_tooltip_text(_('Start'))
        start_button.get_style_context().add_class('flat')

        magic_packet_sent_text = _('Sent magic packet to {name}').format(name=wol_client.name)

        start_button.connect('clicked', lambda _: (
            wol_client.send_magic_packet(),
            self.toaster.add_toast(Adw.Toast.new(magic_packet_sent_text))
        ))

        new_row.add_suffix(start_button)

        self.remotes_list.insert(new_row, -1)


    @Gtk.Template.Callback()
    def spawn_add_remote_dialog(self, _action):
        """Open the add dialog when the add button is clicked."""
        def add_button_on_click(new_client):
            self.wol_clients.add_wol_client(new_client)
            self._add_wol_client_to_list(new_client)
            self.toaster.add_toast(Adw.Toast.new(_('Remote added')))

        dialog = AddDialogBox(add_function=add_button_on_click)

        dialog.present(self)
        dialog.name_entry.grab_focus()

    def spawn_edit_remote_dialog(self, client, new_row):
        """Open the add dialog when the add button is clicked."""
        def edit_button_on_click(edited_client):
            old_name, old_mac, old_port, old_hostname = client.name, client.mac_address, client.port, client.hostname

            def revert():
                client.name, client.mac_address, client.port, client.hostname = old_name, old_mac, old_port, old_hostname
                new_row.set_title(old_name)
                new_row.set_subtitle(client.get_subtitle())
                self._reset_status_dot(new_row)
                self.wol_clients.save_settings()

            client.name, client.mac_address, client.port, client.hostname = edited_client.name, edited_client.mac_address, edited_client.port, edited_client.hostname
            new_row.set_title(client.name)
            new_row.set_subtitle(client.get_subtitle())
            self._reset_status_dot(new_row)
            self.wol_clients.save_settings()

            edited_toast = Adw.Toast.new(_('{name} edited').format(name=client.name))
            edited_toast.set_button_label(_('Undo'))
            edited_toast.connect('button-clicked', lambda _: revert())

            self.toaster.add_toast(edited_toast)

        # delete button
        delete_button = Gtk.Button.new_from_icon_name('edit-delete-symbolic')
        delete_button.set_tooltip_text(_('Delete'))
        delete_button.get_style_context().add_class('flat')

        def delete_button_on_click():
            position = self.wol_clients.remove_wol_client(client)
            deleted_toast = Adw.Toast.new(_('{name} removed').format(name=client.name))
            deleted_toast.set_button_label(_('Undo'))
            deleted_toast.connect('button-clicked', lambda _: (
                self.wol_clients.add_wol_client_at_position(client, position),
                self.remotes_list.insert(new_row, position),
            ))
            self.remotes_list.remove(new_row)
            self.toaster.add_toast(deleted_toast)

            if not self.wol_clients.wol_clients:
                self._show_no_items(True)

        # adw computer icon
        icon = Gtk.Image.new_from_icon_name('computer')
        icon.get_style_context().add_class('icon-dropshadow')
        icon.set_pixel_size(128)
        icon.set_margin_bottom(12)

        dialog = AddDialogBox(add_function=edit_button_on_click)
        dialog.cancel_button.connect('clicked', lambda _: delete_button_on_click())
        dialog.cancel_button.set_label(_('Delete'))
        dialog.cancel_button.get_style_context().add_class('destructive-action')

        dialog.content_box.prepend(icon)

        dialog.set_title(_('Edit Remote'))

        dialog.name_entry.set_text(client.name)
        dialog.mac_entry.set_text(client.get_mac_address())
        dialog.port_entry.set_value(client.port)
        dialog.hostname_entry.set_text(client.hostname)

        dialog.present(self)
        dialog.name_entry.grab_focus()
