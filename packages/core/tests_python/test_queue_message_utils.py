import unittest

from google.protobuf.wrappers_pb2 import StringValue

from core.queue.message_utils import QueueMessageUtils
from core.websocket.message_utils import WebsocketMessageUtils

STRING_VALUE_TYPE = "google.protobuf.StringValue"


class QueueMessageUtilsTest(unittest.TestCase):
    def test_a_message_is_packed_under_its_full_name(self) -> None:
        envelope = QueueMessageUtils.pack(StringValue(value="hello"))
        self.assertEqual(envelope.header.type, STRING_VALUE_TYPE)
        self.assertTrue(envelope.header.id)
        self.assertTrue(envelope.header.HasField("timestamp"))
        unpacked = StringValue()
        self.assertTrue(envelope.payload.Unpack(unpacked))
        self.assertEqual(unpacked.value, "hello")

    def test_every_envelope_has_its_own_id(self) -> None:
        first = QueueMessageUtils.pack(StringValue(value="a"))
        second = QueueMessageUtils.pack(StringValue(value="a"))
        self.assertNotEqual(first.header.id, second.header.id)


class WebsocketMessageUtilsTest(unittest.TestCase):
    def test_a_message_is_packed_under_its_full_name(self) -> None:
        envelope = WebsocketMessageUtils.pack(StringValue(value="hello"))
        self.assertEqual(envelope.header.type, STRING_VALUE_TYPE)
        self.assertTrue(envelope.header.id)
        self.assertTrue(envelope.header.HasField("timestamp"))
        unpacked = StringValue()
        self.assertTrue(envelope.payload.Unpack(unpacked))
        self.assertEqual(unpacked.value, "hello")
