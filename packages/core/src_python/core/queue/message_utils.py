"""
Packing a message for a queue.
"""

import uuid
from datetime import UTC, datetime

from google.protobuf.message import Message
from idl.core.dto.queue_pb2 import QueueMessageEnvelope


class QueueMessageUtils:
    """
    The one place a queue message's header is assembled.
    """

    @staticmethod
    def pack(message: Message) -> QueueMessageEnvelope:
        """
        This message in an envelope: a fresh id, the message's full type name,
        the time of packing, and the message as the payload.
        """
        envelope = QueueMessageEnvelope()
        envelope.header.id = str(uuid.uuid4())
        envelope.header.type = message.DESCRIPTOR.full_name
        envelope.header.timestamp.FromDatetime(datetime.now(UTC))
        envelope.payload.Pack(message)
        return envelope
