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

        self.set_title('Awake on LAN')

        XDG_CONFIG_HOME = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))

        self.wol_clients = SettingsManager(base_path=XDG_CONFIG_HOME)
        self.wol_clients.load_settings()

        self.remotes_list.get_style_context().add_class('boxed-list')

        self.get_application().create_action(
            'add', lambda *_: self.spawn_add_remote_dialog(None), ['<primary>n']
        )

        self.get_application().create_action(
            'view-config', lambda *_: os.system(f'xdg-open {self.wol_clients.settings_file}'), ['<primary>m']
        )

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

        # delete button
        delete_button = Gtk.Button.new_from_icon_name('edit-delete-symbolic')
        delete_button.set_tooltip_text('Delete')
        delete_button.get_style_context().add_class('flat')

        def delete_button_on_click():
            position = self.wol_clients.remove_wol_client(wol_client)
            deleted_toast = Adw.Toast.new(f'{wol_client.name} removed')
            deleted_toast.set_button_label('Undo')
            deleted_toast.connect('button-clicked', lambda _: (
                self.wol_clients.add_wol_client_at_position(wol_client, position),
                self.remotes_list.insert(new_row, position),
            ))
            self.remotes_list.remove(new_row)
            self.toaster.add_toast(deleted_toast)

        delete_button.connect('clicked', lambda _: delete_button_on_click())

        new_row.add_suffix(delete_button)

        # create start button
        start_button = Gtk.Button.new_from_icon_name('media-playback-start-symbolic')
        start_button.set_tooltip_text('Start')
        start_button.get_style_context().add_class('flat')

        start_button.connect('clicked', lambda _: (
            wol_client.send_magic_packet(),
            self.toaster.add_toast(Adw.Toast.new(f'Sent magic packet to {wol_client.name}'))
        ))

        new_row.add_suffix(start_button)


        self.remotes_list.insert(new_row, -1)


    @Gtk.Template.Callback()
    def spawn_add_remote_dialog(self, action):
        """Open the add dialog when the add button is clicked."""
        def add_button_on_click(new_client):
            self.wol_clients.add_wol_client(new_client)
            self._add_wol_client_to_list(new_client)
            self.toaster.add_toast(Adw.Toast.new('Remote added'))

        dialog = AddDialogBox(add_function=add_button_on_click)

        dialog.present(self)
        dialog.name_entry.grab_focus()
