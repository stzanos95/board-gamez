"""
Messages received through Redis pub/sub.
"""

from collections.abc import AsyncIterator

from idl.core.dto.queue_pb2 import QueueMessageEnvelope
from redis.asyncio import Redis

from core.queue.base_queue_consumer import BaseQueueConsumer
from core.queue.config import RedisQueueConfig
from core.queue.redis.channel_names import RedisChannelNames
from core.queue.redis.pubsub_message import RedisPubsubMessages


class RedisQueueConsumer(BaseQueueConsumer):
    """
    Every subscription, against one Redis instance.

    Holds its own client and one pub/sub connection, built from the settings it
    is given. Subscription acknowledgements the connection answers with are
    dropped before a message reaches a caller.
    """

    def __init__(self, config: RedisQueueConfig) -> None:
        self._channel_prefix = config.channel_prefix
        self._client = Redis(host=config.host, port=config.port, db=config.database)
        self._pubsub = self._client.pubsub()

    async def subscribe(self, channel: str) -> None:
        await self._pubsub.subscribe(RedisChannelNames.get_prefixed(self._channel_prefix, channel))

    async def unsubscribe(self, channel: str) -> None:
        await self._pubsub.unsubscribe(
            RedisChannelNames.get_prefixed(self._channel_prefix, channel)
        )

    async def messages(self) -> AsyncIterator[QueueMessageEnvelope]:
        async for raw in self._pubsub.listen():
            envelope = RedisPubsubMessages.get_envelope(raw)
            if envelope is not None:
                yield envelope

    async def close(self) -> None:
        # Dropping every subscription is what ends `listen`, and closing the
        # client disconnects the pool the pub/sub connection was drawn from.
        await self._pubsub.unsubscribe()
        await self._client.aclose()
