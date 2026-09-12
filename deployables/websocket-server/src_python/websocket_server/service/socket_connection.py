"""
What a socket carries from its upgrade to its close.
"""

from dataclasses import dataclass

from websocket_server.service.socketify_client import SocketifyClient


@dataclass(slots=True)
class SocketConnection:
    """
    The channel a socket was opened for, and the client it became.

    Attached to the socket at upgrade time and read back at open and at close.
    Mutable: `client` does not exist until the socket opens, which is after the
    upgrade that creates this record, and close is where it is read.
    """

    channel: str
    client: SocketifyClient | None = None
