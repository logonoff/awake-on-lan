# settings_manager.py
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
from .wol_client import WolClient

class SettingsManager:
    """Settings and configuration manager for the application."""
    wol_clients: list[WolClient]
    settings_file: str


    def __init__(self, base_path: str):
        self.wol_clients = []
        self.settings_file = f'{base_path}/co.logonoff.summon.settings.txt'


    def save_settings(self):
        """Save the settings to the settings file."""
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            for client in self.wol_clients:
                f.write(str(client) + '\n')


    def load_settings(self):
        """Load the settings from the settings file."""
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                self.wol_clients = [WolClient.init_from_json(line) for line in f if line.strip()]
        except FileNotFoundError:
            print(f'Settings file not found, creating a new one at {self.settings_file}')
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)


    def add_wol_client(self, client: WolClient):
        """Add a new WolClient to the list and save the settings."""
        self.wol_clients.append(client)
        self.save_settings()


    def remove_wol_client(self, client: WolClient):
        """Remove a WolClient from the list and save the settings."""
        self.wol_clients.remove(client)
        self.save_settings()
