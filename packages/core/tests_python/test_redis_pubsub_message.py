import unittest

from google.protobuf.wrappers_pb2 import StringValue
from idl.core.dto.queue_pb2 import QueueMessageEnvelope, QueueMessageHeader

from core.queue.redis.channel_names import RedisChannelNames
from core.queue.redis.pubsub_message import RedisPubsubMessages

MESSAGE_ID = "m-1"
MESSAGE_TYPE = "example.Thing"
PREFIX = "gamez"
CHANNEL = "table:t-1"


def envelope_bytes() -> bytes:
    envelope = QueueMessageEnvelope(header=QueueMessageHeader(id=MESSAGE_ID, type=MESSAGE_TYPE))
    envelope.payload.Pack(StringValue(value="hello"))
    return envelope.SerializeToString()


class RedisPubsubMessageTest(unittest.TestCase):
    """
    What the redis library hands a listener, and what is made of it.
    """

    def test_a_published_message_is_opened_into_its_envelope(self) -> None:
        envelope = RedisPubsubMessages.get_envelope(
            {"type": "message", "channel": b"gamez:table:t-1", "data": envelope_bytes()}
        )
        assert envelope is not None
        self.assertEqual(envelope.header.id, MESSAGE_ID)
        self.assertEqual(envelope.header.type, MESSAGE_TYPE)

    def test_a_subscription_acknowledgement_is_not_a_message(self) -> None:
        envelope = RedisPubsubMessages.get_envelope(
            {"type": "subscribe", "channel": b"gamez:table:t-1", "data": 1}
        )
        self.assertIsNone(envelope)

    def test_an_entry_without_bytes_is_not_a_message(self) -> None:
        self.assertIsNone(RedisPubsubMessages.get_envelope({"type": "message", "data": "x"}))

    def test_the_channel_is_read_as_text(self) -> None:
        self.assertEqual(
            RedisPubsubMessages.get_channel({"type": "message", "channel": b"gamez:table:t-1"}),
            "gamez:table:t-1",
        )
        self.assertEqual(RedisPubsubMessages.get_channel({"channel": "gamez:lobby"}), "gamez:lobby")
        self.assertIsNone(RedisPubsubMessages.get_channel({"type": "message"}))


class RedisChannelNamesTest(unittest.TestCase):
    def test_a_channel_is_kept_under_the_prefix(self) -> None:
        self.assertEqual(RedisChannelNames.get_prefixed(PREFIX, CHANNEL), "gamez:table:t-1")

    def test_a_channel_is_read_back_from_under_the_prefix(self) -> None:
        self.assertEqual(RedisChannelNames.get_unprefixed(PREFIX, "gamez:table:t-1"), CHANNEL)

    def test_a_channel_under_another_prefix_is_not_read(self) -> None:
        self.assertIsNone(RedisChannelNames.get_unprefixed(PREFIX, "other:table:t-1"))
        self.assertIsNone(RedisChannelNames.get_unprefixed(PREFIX, "gamez"))
