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

import os
import re
import select
import socket
import struct
import json
import time
import ipaddress
from typing import Union

class WolClient:
    """
    A class that represents a wake on lan client.
    """
    mac_address: bytes
    name: str
    port: int
    hostname: str

    def __init__(self, mac_address: Union[bytes, str], name: str, hostname: str = "", port: int = 7):
        if isinstance(mac_address, str):
            self.mac_address = bytes.fromhex(
                ''.join(char for char in mac_address if char.isalnum())
            )
        elif isinstance(mac_address, bytes):
            self.mac_address = mac_address

        self.name = name
        self.port = int(port)
        self.hostname = hostname


    @staticmethod
    def init_from_json(json_str: str):
        """Initialize a new WolClient object from a JSON string."""
        return WolClient(**json.loads(json_str))


    @staticmethod
    def is_valid_mac_address(mac_address: str) -> bool:
        """Check if a MAC address is valid for usage in the __init__ method."""
        cleaned = ''.join(char for char in mac_address if char.isalnum())
        return len(cleaned) == 12 and all(char in '0123456789abcdefABCDEF' for char in cleaned)


    @staticmethod
    def is_valid_hostname(hostname: str) -> bool:
        """Check if an IP address or hostname is valid for usage in the __init__ method.

        Source: https://stackoverflow.com/a/2532344
        """
        if len(hostname) > 255:
            return False
        try:
            ipaddress.ip_address(hostname)
            return True
        except ValueError:
            pass

        if hostname[-1] == ".":
            hostname = hostname[:-1] # strip exactly one dot from the right, if present
        allowed = re.compile(r"(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
        return all(allowed.match(x) for x in hostname.split("."))

    @staticmethod
    def format_mac(mac_address: bytes) -> str:
        """Get a friendly string representation of the MAC address."""
        mac = mac_address.hex()
        return ':'.join(mac[i:i+2] for i in range(0, len(mac), 2))


    def get_mac_address(self) -> str:
        """Get a friendly string representation of the MAC address."""
        return WolClient.format_mac(self.mac_address)


    def send_magic_packet(self):
        """Send a Wake-on-LAN magic packet to the specified MAC address.

        Source: https://en.wikipedia.org/wiki/Wake-on-LAN#Creating_and_sending_the_magic_packet
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        magic = b"\xff" * 6 + self.mac_address * 16
        s.sendto(magic, ((self.hostname or "<broadcast>"), self.port))
        s.close()


    @staticmethod
    def _checksum(data: bytes) -> int:
        """Compute the RFC 1071 Internet checksum of the given data."""
        if len(data) % 2:
            data += b"\x00"
        total = sum(struct.unpack(f"!{len(data) // 2}H", data))
        total = (total >> 16) + (total & 0xffff)
        total += total >> 16
        return ~total & 0xffff


    def is_online(self, timeout: float = 1.0) -> bool:
        """Check whether the remote answers ICMP echo requests within the timeout."""
        if not self.hostname:
            return False

        try:
            addresses = socket.getaddrinfo(self.hostname, None, socket.AF_INET)
        except OSError:
            return False
        if not addresses:
            return False
        address = addresses[0][4][0]

        identifier = os.getpid() & 0xffff
        header = struct.pack("!BBHHH", 8, 0, 0, identifier, 1)
        packet = struct.pack("!BBHHH", 8, 0, WolClient._checksum(header), identifier, 1)

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_ICMP) as sock:
                sock.sendto(packet, (address, 0))
                deadline = time.monotonic() + timeout
                while True:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        return False
                    readable, _, _ = select.select([sock], [], [], remaining)
                    if not readable:
                        return False
                    data, _ = sock.recvfrom(1024)
                    if not data:
                        continue
                    # some kernels prepend the IPv4 header
                    offset = 20 if len(data) >= 28 and data[0] >> 4 == 4 else 0
                    if data[offset] == 0:  # ICMP echo reply
                        return True
        except OSError:
            return False


    def get_subtitle(self) -> str:
        """Get a readable subtitle for a WolClient, including the hostname/mac/port"""
        subtitle = self.get_mac_address()

        if self.hostname:
            subtitle += f" ({self.hostname}:{self.port})"
        elif self.port != 7:
            subtitle += f" ({_('Port')} {self.port})"

        return subtitle

    def __eq__(self, other):
        return self.mac_address == other.mac_address


    def __str__(self):
        return json.dumps({
            'mac_address': self.get_mac_address(),
            'name': self.name,
            'port': self.port,
            'hostname': self.hostname
        })
