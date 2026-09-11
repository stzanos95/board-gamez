"""
What a move type implies.
"""

from idl.chess.model.move_pb2 import (
    MOVE_TYPE_CAPTURE,
    MOVE_TYPE_EN_PASSANT,
    MOVE_TYPE_PROMOTION,
    MOVE_TYPE_PROMOTION_CAPTURE,
    MoveType,
)

CAPTURING_MOVE_TYPES: tuple[MoveType, ...] = (
    MOVE_TYPE_CAPTURE,
    MOVE_TYPE_EN_PASSANT,
    MOVE_TYPE_PROMOTION_CAPTURE,
)
PROMOTING_MOVE_TYPES: tuple[MoveType, ...] = (MOVE_TYPE_PROMOTION, MOVE_TYPE_PROMOTION_CAPTURE)


class MoveTypes:
    """
    What is true of a move type.
    """

    @staticmethod
    def is_capture(move_type: MoveType) -> bool:
        return move_type in CAPTURING_MOVE_TYPES

    @staticmethod
    def is_promotion(move_type: MoveType) -> bool:
        return move_type in PROMOTING_MOVE_TYPES
