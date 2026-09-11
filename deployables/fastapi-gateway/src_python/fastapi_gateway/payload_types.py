"""
The payload types this gateway can translate.

A game's state and actions cross the platform's paths as `google.protobuf.Any`.
Translating one between JSON and a message resolves its `@type` against the
types this process has imported, so a type that is not imported here cannot be
sent or answered as JSON. One line per game.
"""

from idl.chess.model import action_pb2, game_pb2

PAYLOAD_MODULES = (action_pb2, game_pb2)


class PayloadTypeRegistry:
    """
    What the payload modules imported above declare.
    """

    @staticmethod
    def get_type_names() -> tuple[str, ...]:
        """
        The full name of every message a payload may carry.
        """
        return tuple(
            descriptor.full_name
            for module in PAYLOAD_MODULES
            for descriptor in module.DESCRIPTOR.message_types_by_name.values()
        )
