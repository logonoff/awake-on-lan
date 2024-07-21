# add_dialog.py
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

@Gtk.Template(resource_path='/co/logonoff/summon/add_dialog.ui')
class AddDialogBox(Adw.Dialog):
    __gtype_name__ = 'AddDialogBox'

    header: Adw.HeaderBar = Gtk.Template.Child()
    name_entry: Adw.EntryRow = Gtk.Template.Child()
    mac_entry: Adw.EntryRow = Gtk.Template.Child()
    port_entry: Adw.SpinRow = Gtk.Template.Child()
    add_button: Gtk.Button = Gtk.Template.Child()
    cancel_button: Gtk.Button = Gtk.Template.Child()

    parent: Adw.ApplicationWindow

    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)

        self.parent = parent

        self.cancel_button.connect('clicked', self.cancel_button_on_click)

        self.add_button.set_sensitive(False)
        self.add_button.get_style_context().add_class('suggested-action')

        self.name_entry.connect('changed', lambda _: self.validate_entry())
        self.mac_entry.connect('changed', lambda _: self.validate_entry())

    def generate_wol_client(self):
        return WolClient(mac_address=self.mac_entry.get_text(),
                         name=self.name_entry.get_text(),
                         port=self.port_entry.get_value())

    def validate_entry(self):
        """Validate the entry fields and enable the add button if valid."""
        self.add_button.set_sensitive(self.name_entry.get_text() and WolClient.is_valid_mac_address(self.mac_entry.get_text()))

    def cancel_button_on_click(self, action):
        """Close the dialog."""
        self.close()
