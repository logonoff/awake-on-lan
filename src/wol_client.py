# wol_client.py
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

import socket
import json
from typing import Union

class WolClient:
    """
    A class that represents a wake on lan client.
    """
    mac_address: bytes
    name: str
    port: int

    def __init__(self, mac_address: Union[bytes, str], name: str, port: int = 7):
        if isinstance(mac_address, str):
            self.mac_address = bytes.fromhex(
                ''.join(char for char in mac_address if char.isalnum())
            )
        elif isinstance(mac_address, bytes):
            self.mac_address = mac_address

        self.name = name
        self.port = int(port)


    @staticmethod
    def init_from_json(json_str: str):
        """Initialize a new WolClient object from a JSON string."""
        return WolClient(**json.loads(json_str))


    @staticmethod
    def is_valid_mac_address(mac_address: str) -> bool:
        """Check if a MAC address is valid for usage in the __init__ method."""
        cleaned = ''.join(char for char in mac_address if char.isalnum())
        return len(cleaned) == 12 and all(char in '0123456789abcdefABCDEF' for char in cleaned)


    def get_mac_address(self) -> str:
        """Get a friendly string representation of the MAC address."""
        mac = self.mac_address.hex()
        return ':'.join(mac[i:i+2] for i in range(0, len(mac), 2))


    def send_magic_packet(self):
        """Send a Wake-on-LAN magic packet to the specified MAC address.

        Source: https://en.wikipedia.org/wiki/Wake-on-LAN#Creating_and_sending_the_magic_packet
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        magic = b"\xff" * 6 + self.mac_address * 16
        s.sendto(magic, ("<broadcast>", self.port))
        s.close()


    def __eq__(self, other):
        return self.mac_address == other.mac_address


    def __str__(self):
        return json.dumps({
            'mac_address': self.get_mac_address(),
            'name': self.name,
            'port': self.port
        })
