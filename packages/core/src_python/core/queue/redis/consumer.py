"""
Messages received through Redis pub/sub.
"""

import asyncio
import contextlib
from collections.abc import AsyncIterator

from redis.asyncio import Redis

from core.queue.base_queue_consumer import BaseQueueConsumer
from core.queue.config import RedisQueueConfig
from core.queue.received_message import ReceivedMessage
from core.queue.redis.channel_names import RedisChannelNames
from core.queue.redis.pubsub_message import RedisPubsubMessages

# How long `close` waits for a reader of `messages` to see the last
# unsubscribe before the connection under it is dropped.
CLOSE_GRACE_SECONDS = 5.0


class RedisQueueConsumer(BaseQueueConsumer):
    """
    Every subscription, against one Redis instance.

    Holds its own client and one pub/sub connection, built from the settings it
    is given. Commands on that connection are issued one at a time, so callers
    may subscribe and unsubscribe concurrently. Subscription acknowledgements
    the connection answers with are dropped before a message reaches a caller,
    and so is a message on a channel outside this consumer's prefix.
    """

    def __init__(self, config: RedisQueueConfig) -> None:
        self._channel_prefix = config.channel_prefix
        self._client = Redis(host=config.host, port=config.port, db=config.database)
        self._pubsub = self._client.pubsub()
        self._commands = asyncio.Lock()
        # The pub/sub connection stops yielding when it holds no subscription.
        # This is what `messages` waits on until the next one is made.
        self._has_subscription = asyncio.Event()
        # Set while no reader of `messages` is inside the connection's listener.
        self._idle = asyncio.Event()
        self._idle.set()
        self._closed = False

    async def subscribe(self, channel: str) -> None:
        async with self._commands:
            await self._pubsub.subscribe(
                RedisChannelNames.get_prefixed(self._channel_prefix, channel)
            )
        self._has_subscription.set()

    async def unsubscribe(self, channel: str) -> None:
        async with self._commands:
            await self._pubsub.unsubscribe(
                RedisChannelNames.get_prefixed(self._channel_prefix, channel)
            )

    async def messages(self) -> AsyncIterator[ReceivedMessage]:
        while not self._closed:
            await self._has_subscription.wait()
            if self._closed:
                return
            self._idle.clear()
            try:
                async for raw in self._pubsub.listen():
                    received = self._get_received_message(raw)
                    if received is not None:
                        yield received
            finally:
                self._idle.set()
            # The listener has returned because the last channel was
            # unsubscribed, unless a subscription was made while it was
            # returning.
            if not self._pubsub.subscribed:
                self._has_subscription.clear()

    async def close(self) -> None:
        # Waking `messages` first lets it see `_closed` and return. Dropping
        # every subscription is what ends the listener, and a reader inside it
        # is given time to see that before the client is closed: a connection
        # dropped under the listener is reconnected and resubscribed by the
        # library, which would keep the reader waiting. Closing the client
        # disconnects the pool the pub/sub connection was drawn from.
        self._closed = True
        self._has_subscription.set()
        async with self._commands:
            await self._pubsub.unsubscribe()
        with contextlib.suppress(TimeoutError):
            await asyncio.wait_for(self._idle.wait(), CLOSE_GRACE_SECONDS)
        await self._client.aclose()

    def _get_received_message(self, raw: dict[str, object]) -> ReceivedMessage | None:
        envelope = RedisPubsubMessages.get_envelope(raw)
        if envelope is None:
            return None
        prefixed = RedisPubsubMessages.get_channel(raw)
        if prefixed is None:
            return None
        channel = RedisChannelNames.get_unprefixed(self._channel_prefix, prefixed)
        if channel is None:
            return None
        return ReceivedMessage(channel=channel, envelope=envelope)
