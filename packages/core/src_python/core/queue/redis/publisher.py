"""
Messages sent through Redis pub/sub.
"""

from idl.core.dto.queue_pb2 import QueueMessageEnvelope
from redis.asyncio import Redis

from core.queue.base_queue_publisher import BaseQueuePublisher
from core.queue.config import RedisQueueConfig
from core.queue.redis.channel_names import RedisChannelNames


class RedisQueuePublisher(BaseQueuePublisher):
    """
    Every publish, against one Redis instance.

    Holds its own client, built from the settings it is given. An envelope is
    published as bytes; Redis holds nothing after delivery, so a subscriber that
    was not listening does not receive it.
    """

    def __init__(self, config: RedisQueueConfig) -> None:
        self._channel_prefix = config.channel_prefix
        self._client = Redis(host=config.host, port=config.port, db=config.database)

    async def publish(self, channel: str, envelope: QueueMessageEnvelope) -> None:
        await self._client.publish(
            RedisChannelNames.get_prefixed(self._channel_prefix, channel),
            envelope.SerializeToString(),
        )

    async def close(self) -> None:
        await self._client.aclose()
