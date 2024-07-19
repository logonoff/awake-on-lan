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

from gi.repository import Adw
from gi.repository import Gtk
from .wol_client import WolClient
from .settings_manager import SettingsManager
import os

@Gtk.Template(resource_path='/co/logonoff/summon/add_dialog.glade')
class AddDialogBox(Gtk.Dialog):
    __gtype_name__ = 'AddDialogBox'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_button.connect('clicked', self.summon_application_add_action)

    def summon_application_add_action(self, action):
        """Callback for the summon_application_add action."""
        print('hello')

@Gtk.Template(resource_path='/co/logonoff/summon/window.ui')
class SummonWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'SummonWindow'

    GtkScrolledWindow = Gtk.Template.Child()
    add_button: Gtk.Button = Gtk.Template.Child()
    remotes_list: Gtk.ListBox = Gtk.Template.Child()
    wol_clients: SettingsManager

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        XDG_CONFIG_HOME = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))

        self.wol_clients = SettingsManager(base_path=XDG_CONFIG_HOME)
        self.wol_clients.load_settings()

        self.remotes_list.get_style_context().add_class('boxed-list')

        for client in self.wol_clients.wol_clients:
            self.add_wol_client_to_list(client)

        self.add_button.connect('clicked', self.summon_application_add_action)


    def add_wol_client_to_list(self, wol_client):
        """Add a new WolClient to the list and update the view."""
        new_row = Adw.ActionRow.new()
        new_row.set_title(wol_client.name)
        new_row.set_subtitle(wol_client.get_mac_address())
        new_row.get_style_context().add_class('AdwActionRow')

        # create start button
        start_button = Gtk.Button.new_from_icon_name('media-playback-start-symbolic')
        start_button.set_tooltip_text('Start')
        start_button.get_style_context().add_class('flat')

        new_row.add_suffix(start_button)
        start_button.connect('clicked', lambda _: wol_client.send_magic_packet())

        self.remotes_list.insert(new_row, -1)


    def summon_application_add_action(self, action):
        """Show a dialog to add a new application and save the result
        """
        # create new dialog
        dialog = Adw.Dialog.new()

        # set dialog title
        dialog.set_title('Add new remote')

        # add button
        add_button = Gtk.Button(label='Save')
        add_button.get_style_context().add_class('suggested-action')
        add_button.set_sensitive(False) # disable button until data valid

        def add_button_on_click():
            self.wol_clients.add_wol_client(generate_wol_client())
            self.add_wol_client_to_list(self.wol_clients.wol_clients[-1])
            dialog.close()

        add_button.connect('clicked', lambda _: add_button_on_click())

        # cancel button
        cancel_button = Gtk.Button(label='Cancel')
        cancel_button.connect('clicked', lambda _: dialog.close())

        # create a new grid
        view = Adw.ToolbarView.new()
        dialog.set_child(view)

        header = Adw.HeaderBar.new()
        header.set_show_title(True)
        header.pack_start(cancel_button)
        header.pack_end(add_button)
        header.set_show_start_title_buttons(False)
        header.set_show_end_title_buttons(False)
        header.get_style_context().add_class('flat')

        view.add_top_bar(header)

        # create gtklistbox
        listbox = Gtk.ListBox.new()
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        listbox.get_style_context().add_class('boxed-list')

        # add padding
        listbox.set_margin_top(24)
        listbox.set_margin_bottom(24)
        listbox.set_margin_start(24)
        listbox.set_margin_end(24)

        view.set_content(listbox)

        # create a new entry
        name_entry = Adw.EntryRow.new()
        name_entry.set_title('Name')
        name_entry.connect('changed', lambda _:
            add_button.set_sensitive(validate_entry()))
        listbox.insert(name_entry, -1)

        # create a new label
        mac_entry = Adw.EntryRow.new()
        mac_entry.set_title('MAC address')
        mac_entry.connect('changed', lambda _:
            add_button.set_sensitive(validate_entry()))
        listbox.insert(mac_entry, -1)

        # create a new label
        port_entry = Adw.SpinRow.new_with_range(0, 65535, 1)
        port_entry.set_title('Port number')
        port_entry.set_value(9)
        listbox.insert(port_entry, -1)

        def generate_wol_client():
            return WolClient(mac_address=mac_entry.get_text(),
                             name=name_entry.get_text(),
                             port=port_entry.get_value())

        def validate_entry():
            return name_entry.get_text() and WolClient.is_valid_mac_address(mac_entry.get_text())

        # destroy the dialog
        dialog.present(self)
