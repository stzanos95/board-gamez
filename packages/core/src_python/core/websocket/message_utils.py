"""
Packing a message for a socket.
"""

import uuid
from datetime import UTC, datetime

from google.protobuf.message import Message
from idl.core.dto.websocket_pb2 import WebsocketMessageEnvelope


class WebsocketMessageUtils:
    """
    The one place a socket frame's header is assembled.
    """

    @staticmethod
    def pack(message: Message) -> WebsocketMessageEnvelope:
        """
        This message in a frame: a fresh id, the message's full type name, the
        time of packing, and the message as the payload.
        """
        envelope = WebsocketMessageEnvelope()
        envelope.header.id = str(uuid.uuid4())
        envelope.header.type = message.DESCRIPTOR.full_name
        envelope.header.timestamp.FromDatetime(datetime.now(UTC))
        envelope.payload.Pack(message)
        return envelope
