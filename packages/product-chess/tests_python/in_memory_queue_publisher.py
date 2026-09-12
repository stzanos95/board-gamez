"""
A publisher that keeps what it was given, so a controller test can read it back.
"""

from dataclasses import dataclass

from core.queue.base_queue_publisher import BaseQueuePublisher
from idl.core.dto.queue_pb2 import QueueMessageEnvelope


@dataclass(frozen=True, slots=True)
class PublishedMessage:
    """
    One envelope, and the channel it was published on.
    """

    channel: str
    envelope: QueueMessageEnvelope


class InMemoryQueuePublisher(BaseQueuePublisher):
    """
    Every publish, in order.
    """

    def __init__(self) -> None:
        self.published: list[PublishedMessage] = []

    async def publish(self, channel: str, envelope: QueueMessageEnvelope) -> None:
        self.published.append(PublishedMessage(channel=channel, envelope=envelope))

    async def close(self) -> None:
        return None

    def get_types_on(self, channel: str) -> list[str]:
        """
        The full type name of every message published on this channel, in
        order.
        """
        return [
            published.envelope.header.type
            for published in self.published
            if published.channel == channel
        ]
