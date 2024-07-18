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

        for client in self.wol_clients.wol_clients:
            self.add_wol_client_to_list(client)

        self.add_button.connect('clicked', self.summon_application_add_action)


    def add_wol_client_to_list(self, wol_client):
        """Add a new WolClient to the list and update the view."""
        new_row = Adw.ActionRow.new()
        new_row.set_title(wol_client.name)
        new_row.set_subtitle(wol_client.get_mac_address())

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
        dialog.set_title('Add new application')

        # create a new grid
        grid = Gtk.Grid.new()
        dialog.set_child(grid)

        header = Adw.HeaderBar.new()
        header.set_show_title(False)
        header.get_style_context().add_class('flat')

        grid.attach(header, 0, 0, 2, 1)

        # create a new label
        label = Gtk.Label(label='Name')
        grid.attach(label, 0, 1, 1, 1)

        # create a new entry
        name_entry = Gtk.Entry()
        grid.attach(name_entry, 1, 1, 1, 1)

        # create a new label
        label = Gtk.Label(label='MAC Address')
        grid.attach(label, 0, 2, 1, 1)

        def generate_wol_client():
            return WolClient(mac_address=mac_entry.get_text(),
                             name=name_entry.get_text())

        # create a new entry
        mac_entry = Gtk.Entry()
        grid.attach(mac_entry, 1, 2, 1, 1)

        # create a new button
        add_button = Gtk.Button(label='Add')
        add_button.get_style_context().add_class('suggested-action')
        grid.attach(add_button, 0, 3, 2, 1)

        def add_button_on_click():
            self.wol_clients.add_wol_client(generate_wol_client())
            self.add_wol_client_to_list(self.wol_clients.wol_clients[-1])
            dialog.close()

        # connect the button to the dialog response signal
        add_button.connect('clicked', lambda _: add_button_on_click())

        # destroy the dialog
        dialog.present(self)
