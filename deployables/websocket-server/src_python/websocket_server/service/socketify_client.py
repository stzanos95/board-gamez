"""
A client reached over a socketify socket.
"""

from socketify import OpCode

from websocket_server.controller.base_client import BaseClient
from websocket_server.service.socketify_types import SocketifyWebSocket


class SocketifyClient(BaseClient):
    """
    One open socket, sent frames as binary.

    Holds the socket it was opened with. The socket is valid until its close
    handler has run, and nothing sends to a client after it has been detached.
    """

    def __init__(self, websocket: SocketifyWebSocket) -> None:
        self._websocket = websocket

    def send(self, frame: bytes) -> None:
        self._websocket.send(frame, OpCode.BINARY)
