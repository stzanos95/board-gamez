"""
The operations any consumer of messages must answer.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from idl.core.dto.queue_pb2 import QueueMessageEnvelope


class BaseQueueConsumer(ABC):
    """
    Where messages are received from, whatever carries them.

    Subscribe to channels, then read `messages` as they arrive. Transport only:
    nothing here reads a payload, and a message that arrived while nothing was
    subscribed is not seen. What a message means is read off its header.
    """

    @abstractmethod
    async def subscribe(self, channel: str) -> None:
        """
        Start receiving what is published on this channel.
        """

    @abstractmethod
    async def unsubscribe(self, channel: str) -> None:
        """
        Stop receiving what is published on this channel.
        """

    @abstractmethod
    def messages(self) -> AsyncIterator[QueueMessageEnvelope]:
        """
        Every envelope published on a subscribed channel, as it arrives. Ends
        when the consumer is closed.
        """

    @abstractmethod
    async def close(self) -> None:
        """
        Drop every subscription and release the connection to the broker.
        """
