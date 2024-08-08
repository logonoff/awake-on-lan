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

from typing import Callable
from gi.repository import Adw
from gi.repository import Gtk
from .wol_client import WolClient

@Gtk.Template(resource_path='/co/logonoff/awakeonlan/add_dialog.ui')
class AddDialogBox(Adw.Dialog):
    """Dialog box to add a new WolClient. Note that the add function is bring
    your own (to avoid a circular import)."""

    __gtype_name__ = 'AddDialogBox'

    header: Adw.HeaderBar = Gtk.Template.Child()
    name_entry: Adw.EntryRow = Gtk.Template.Child()
    mac_entry: Adw.EntryRow = Gtk.Template.Child()
    port_entry: Adw.SpinRow = Gtk.Template.Child()
    add_button: Gtk.Button = Gtk.Template.Child()
    cancel_button: Gtk.Button = Gtk.Template.Child()
    content: Gtk.ListBox = Gtk.Template.Child()
    content_box: Gtk.Box = Gtk.Template.Child()

    parent: Adw.ApplicationWindow

    def __init__(self, add_function: Callable[[WolClient], None], **kwargs):
        super().__init__(**kwargs)

        def add_if_valid():
            if self.is_valid_entry():
                add_function(self.generate_wol_client())
                self.close()

        self.cancel_button.connect('clicked', lambda _: self.close())

        self.add_button.set_sensitive(False)
        self.add_button.get_style_context().add_class('suggested-action')
        self.add_button.connect('clicked', lambda _: add_if_valid())

        self.name_entry.connect('changed', lambda _: self.validate_entry())
        self.mac_entry.connect('changed', lambda _: self.validate_entry())

        self.name_entry.connect('apply', lambda _: add_if_valid())
        self.mac_entry.connect('apply', lambda _: add_if_valid())
        self.name_entry.connect('apply', lambda _: add_if_valid())

        self.content.get_style_context().add_class('boxed-list')


    def generate_wol_client(self) -> WolClient:
        """Return a new WolClient object with the data from the dialog."""
        return WolClient(mac_address=self.mac_entry.get_text(),
                         name=self.name_entry.get_text(),
                         port=self.port_entry.get_value())

    def is_valid_entry(self) -> bool:
        """Return True if the entry fields are valid."""
        return self.name_entry.get_text() and WolClient.is_valid_mac_address(self.mac_entry.get_text())

    def validate_entry(self):
        """Validate the entry fields and enable the add button if valid."""
        self.add_button.set_sensitive(self.is_valid_entry())
