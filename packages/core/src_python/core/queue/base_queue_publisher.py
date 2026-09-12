"""
The operations any publisher of messages must answer.
"""

from abc import ABC, abstractmethod

from idl.core.dto.queue_pb2 import QueueMessageEnvelope


class BaseQueuePublisher(ABC):
    """
    Where messages are sent, whatever carries them.

    Takes an envelope and a channel, so a caller packs at this boundary.
    Transport only: nothing here reads the payload, and a message published is
    not held for a consumer that is not yet listening.
    """

    @abstractmethod
    async def publish(self, channel: str, envelope: QueueMessageEnvelope) -> None:
        """
        Send this envelope on this channel.
        """

    @abstractmethod
    async def close(self) -> None:
        """
        Release the connection to the broker.
        """
