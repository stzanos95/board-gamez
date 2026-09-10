"""
The channel arguments gRPC accepts, modelled.

gRPC takes its tuning as a sequence of name/value pairs whose names are dotted
strings it defines. This module is the one place those names are written, for
both ends of a call: a server that will not accept a message beyond its limit and
a client that will not receive one are the same setting, and a pair that disagree
fail on whichever side is smaller.
"""

from dataclasses import dataclass

MAX_RECEIVE_MESSAGE_LENGTH = "grpc.max_receive_message_length"
MAX_SEND_MESSAGE_LENGTH = "grpc.max_send_message_length"


@dataclass(frozen=True, slots=True)
class ChannelOptions:
    """
    What one end of a connection will accept and send.

    A message larger than either limit is refused rather than truncated.
    """

    max_receive_message_bytes: int
    max_send_message_bytes: int

    def to_options(self) -> list[tuple[str, int]]:
        """
        The pairs gRPC expects. Keys are data to the library, not fields.
        """
        return [
            (MAX_RECEIVE_MESSAGE_LENGTH, self.max_receive_message_bytes),
            (MAX_SEND_MESSAGE_LENGTH, self.max_send_message_bytes),
        ]
