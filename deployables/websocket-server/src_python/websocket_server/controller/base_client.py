"""
What any connected client must answer.
"""

from abc import ABC, abstractmethod


class BaseClient(ABC):
    """
    One open connection, whatever carries it.

    Transport only: a frame is handed over as bytes, already packed. Nothing
    here knows who is connected or what a frame means.
    """

    @abstractmethod
    def send(self, frame: bytes) -> None:
        """
        Send this frame to the connection.
        """
