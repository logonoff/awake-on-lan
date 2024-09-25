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
from gi.repository import Adw
from gi.repository import Gtk
from .add_dialog import AddDialogBox
from .settings_manager import SettingsManager

@Gtk.Template(resource_path='/co/logonoff/awakeonlan/window.ui')
class awakeonlanWindow(Adw.ApplicationWindow):
    """Main application window."""
    __gtype_name__ = 'awakeonlanWindow'

    add_button: Gtk.Button = Gtk.Template.Child()
    remotes_list: Gtk.ListBox = Gtk.Template.Child()
    no_items: Adw.StatusPage = Gtk.Template.Child()
    toaster: Adw.ToastOverlay = Gtk.Template.Child()
    content_box: Gtk.Box = Gtk.Template.Child()
    wol_clients: SettingsManager

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title(_('Awake on LAN'))

        XDG_CONFIG_HOME = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))

        self.wol_clients = SettingsManager(base_path=XDG_CONFIG_HOME, version=self.get_application().version)
        self.wol_clients.load_settings()

        self.remotes_list.get_style_context().add_class('boxed-list')

        self.get_application().create_action(
            'add', lambda *_: self.spawn_add_remote_dialog(None), ['<primary>n']
        )

        # self.get_application().create_action(
            # 'view-config', lambda *_: os.system(f'xdg-open {self.wol_clients.settings_file}'), ['<primary>m']
        # )

        for client in self.wol_clients.wol_clients:
            self._add_wol_client_to_list(client)


    def _show_no_items(self, show: bool):
        """Show or hide the no items page."""
        if show:
            self.no_items.show()
            self.content_box.set_valign(Gtk.Align.CENTER)
        else:
            self.no_items.hide()
            self.content_box.set_valign(Gtk.Align.FILL)


    def _add_wol_client_to_list(self, wol_client):
        """Add a new WolClient to the list and update the view."""
        self._show_no_items(False)

        new_row = Adw.ActionRow.new()
        new_row.set_title(wol_client.name)
        new_row.set_subtitle(wol_client.get_mac_address())
        new_row.get_style_context().add_class('AdwActionRow')
        new_row.set_activatable(True)

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

        start_button.connect('clicked', lambda _: (
            wol_client.send_magic_packet(),
            self.toaster.add_toast(Adw.Toast.new(_('Sent magic packet to {name}').format(name = wol_client.name)))
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
            old_name, old_mac, old_port = client.name, client.mac_address, client.port

            def revert():
                client.name, client.mac_address, client.port = old_name, old_mac, old_port
                new_row.set_title(old_name)
                new_row.set_subtitle(old_mac)
                self.wol_clients.save_settings()

            client.name, client.mac_address, client.port = edited_client.name, edited_client.mac_address, edited_client.port
            new_row.set_title(client.name)
            new_row.set_subtitle(client.get_mac_address())
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
        dialog.port_entry.set_text(str(client.port))

        dialog.present(self)
        dialog.name_entry.grab_focus()
