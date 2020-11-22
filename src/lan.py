import json, socket

from typing import Sequence

from edgin_around_api import defs

BUFFER_SIZE = 1024


def list_servers() -> Sequence[str]:
    """Lists Edgin' Around servers available in the local network."""

    request = {"name": "edgin_around", "version": defs.VERSION}
    address = ("<broadcast>", defs.PORT_BROADCAST)
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.settimeout(1.0)
    client.sendto(json.dumps(request).encode(), address)

    result = list()
    while True:
        try:
            data, addr = client.recvfrom(BUFFER_SIZE)
            result.append(addr)
        except socket.timeout:
            break

    return result
