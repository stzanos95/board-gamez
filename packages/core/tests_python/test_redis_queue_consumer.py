import asyncio
import unittest
from collections.abc import AsyncIterator

from google.protobuf.wrappers_pb2 import StringValue

from core.queue.config import RedisQueueConfig
from core.queue.message_utils import QueueMessageUtils
from core.queue.redis.consumer import RedisQueueConsumer

CONFIG = RedisQueueConfig(host="localhost", port=6379, database=0, channel_prefix="gamez")
CHANNEL = "table:t-1"
WAIT_SECONDS = 0.05

RawEntries = list[dict[str, object]]


class ScriptedPubsub:
    """
    A pub/sub connection that yields the entries it was given, once, and then
    reports whatever `subscribed` was set to.
    """

    def __init__(self) -> None:
        self.entries: RawEntries = []
        self.subscribed = False
        self.listens = 0

    async def listen(self) -> AsyncIterator[dict[str, object]]:
        self.listens += 1
        for entry in self.entries:
            yield entry
        self.entries = []


def entry(channel: bytes) -> dict[str, object]:
    return {
        "type": "message",
        "channel": channel,
        "data": QueueMessageUtils.pack(StringValue(value="x")).SerializeToString(),
    }


class RedisQueueConsumerTest(unittest.IsolatedAsyncioTestCase):
    """
    What `messages` does around the pub/sub connection: waits while nothing is
    subscribed, strips the prefix, and ends only on close.
    """

    def setUp(self) -> None:
        self.consumer = RedisQueueConsumer(config=CONFIG)
        self.pubsub = ScriptedPubsub()
        # The connection is replaced with a scripted one so no Redis is needed.
        self.consumer._pubsub = self.pubsub  # type: ignore[assignment]

    async def test_nothing_is_read_until_something_is_subscribed(self) -> None:
        self.pubsub.entries = [entry(b"gamez:table:t-1")]
        reader = asyncio.ensure_future(anext(self.consumer.messages()))
        await asyncio.sleep(WAIT_SECONDS)
        self.assertFalse(reader.done())
        self.assertEqual(self.pubsub.listens, 0)
        self.pubsub.subscribed = True
        self.consumer._has_subscription.set()
        received = await reader
        self.assertEqual(received.channel, CHANNEL)
        self.assertEqual(received.envelope.header.type, "google.protobuf.StringValue")

    async def test_a_channel_under_another_prefix_is_dropped(self) -> None:
        self.pubsub.entries = [entry(b"other:table:t-1"), entry(b"gamez:lobby")]
        self.pubsub.subscribed = True
        self.consumer._has_subscription.set()
        received = await anext(self.consumer.messages())
        self.assertEqual(received.channel, "lobby")

    async def test_the_iterator_ends_on_close(self) -> None:
        self.pubsub.subscribed = False
        reader = asyncio.ensure_future(anext(self.consumer.messages()))
        await asyncio.sleep(WAIT_SECONDS)
        self.consumer._closed = True
        self.consumer._has_subscription.set()
        with self.assertRaises(StopAsyncIteration):
            await reader
