"""
The mapping a Redis pub/sub client hands back for each entry it reads.

Models the shape the redis library answers with, so its keys and its kinds are
named once, here, and nowhere else.
"""

from idl.core.dto.queue_pb2 import QueueMessageEnvelope

TYPE_KEY = "type"
CHANNEL_KEY = "channel"
DATA_KEY = "data"
MESSAGE_TYPE = "message"
CHANNEL_ENCODING = "utf-8"


class RedisPubsubMessages:
    """
    What a pub/sub listener's entries carry.
    """

    @staticmethod
    def get_envelope(raw: dict[str, object]) -> QueueMessageEnvelope | None:
        """
        The envelope this entry carries, or None when the entry is a
        subscription acknowledgement or otherwise not a message.

        The mapping's keys are the library's, so `raw` stays a dict here.
        """
        if raw.get(TYPE_KEY) != MESSAGE_TYPE:
            return None
        data = raw.get(DATA_KEY)
        if not isinstance(data, bytes):
            return None
        envelope = QueueMessageEnvelope()
        envelope.ParseFromString(data)
        return envelope

    @staticmethod
    def get_channel(raw: dict[str, object]) -> str | None:
        """
        The full channel name this entry arrived on, prefix included, or None
        when the entry names no channel.
        """
        channel = raw.get(CHANNEL_KEY)
        if isinstance(channel, bytes):
            return channel.decode(CHANNEL_ENCODING)
        if isinstance(channel, str):
            return channel
        return None
