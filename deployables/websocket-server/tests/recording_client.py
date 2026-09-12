"""
A client that keeps what it was sent, so a test can read it back.
"""

from websocket_server.controller.base_client import BaseClient


class RecordingClient(BaseClient):
    """
    Every frame this client was sent, in order.
    """

    def __init__(self) -> None:
        self.frames: list[bytes] = []

    def send(self, frame: bytes) -> None:
        self.frames.append(frame)
