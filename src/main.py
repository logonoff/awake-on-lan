# main.py
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

import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gdk, Gio, Adw
Adw.init() # needed for windows for some reason, otherwise no adwaita styles load
from .window import awakeonlanWindow


class awakeonlanApplication(Adw.Application):
    """The main application singleton class."""
    version: str
    css_loaded = False

    def __init__(self, version: str = '0.0.0'):
        flags = Gio.ApplicationFlags.DEFAULT_FLAGS
        if sys.platform == 'win32':
            flags |= Gio.ApplicationFlags.NON_UNIQUE
        super().__init__(application_id='co.logonoff.awakeonlan',
                         flags=flags)
        self.version = version
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q', '<primary>w'])
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action)

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        if not self.css_loaded:
            self.load_styles()
            self.css_loaded = True
        win = self.props.active_window
        if not win:
            win = awakeonlanWindow(application=self)
        win.present()

    def load_styles(self):
        """Load the application CSS on top of the system theme."""
        provider = Gtk.CssProvider()
        provider.load_from_resource(f'{self.get_resource_base_path()}/style.css')
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def on_about_action(self, widget, _):
        """Callback for the app.about action."""
        about = Adw.AboutDialog.new_from_appdata(f'{self.get_resource_base_path()}/metainfo', self.version)
        about.present(self.props.active_window)

    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        print('app.preferences action activated')

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version):
    """The application's entry point."""
    app = awakeonlanApplication(version=version)
    return app.run(sys.argv)
