"""
What a consumer hands back for each message it reads.
"""

from dataclasses import dataclass

from idl.core.dto.queue_pb2 import QueueMessageEnvelope


@dataclass(frozen=True, slots=True)
class ReceivedMessage:
    """
    One envelope, and the channel it was published on.

    `channel` is the name the caller subscribed with; whatever a broker adds to
    it in transit has been removed.
    """

    channel: str
    envelope: QueueMessageEnvelope
