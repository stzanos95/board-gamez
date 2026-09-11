"""
Castling rights as a set.

The schema carries the rights as a list. Every list this module answers is in
one fixed order, so two equal sets of rights are equal messages.
"""

from idl.chess.model.castling_pb2 import (
    CASTLING_SIDE_KINGSIDE,
    CASTLING_SIDE_QUEENSIDE,
    CastlingRight,
    CastlingRights,
    CastlingSide,
)
from idl.chess.model.piece_pb2 import Color

from chess.core.colors import ALL_COLORS

ALL_CASTLING_SIDES: tuple[CastlingSide, ...] = (CASTLING_SIDE_KINGSIDE, CASTLING_SIDE_QUEENSIDE)


class CastlingRightSets:
    """
    Reading and editing which castles remain available.
    """

    @staticmethod
    def full() -> CastlingRights:
        return CastlingRights(
            available=[
                CastlingRight(color=color, side=side)
                for color in ALL_COLORS
                for side in ALL_CASTLING_SIDES
            ]
        )

    @staticmethod
    def none() -> CastlingRights:
        return CastlingRights()

    @staticmethod
    def allows(rights: CastlingRights, color: Color, side: CastlingSide) -> bool:
        return CastlingRight(color=color, side=side) in rights.available

    @staticmethod
    def without(rights: CastlingRights, right: CastlingRight) -> CastlingRights:
        return CastlingRightSets.canonical(
            CastlingRights(available=[held for held in rights.available if held != right])
        )

    @staticmethod
    def without_color(rights: CastlingRights, color: Color) -> CastlingRights:
        return CastlingRightSets.canonical(
            CastlingRights(available=[held for held in rights.available if held.color != color])
        )

    @staticmethod
    def canonical(rights: CastlingRights) -> CastlingRights:
        """
        The same rights, each at most once, in the one fixed order.
        """
        return CastlingRights(
            available=[
                CastlingRight(color=color, side=side)
                for color in ALL_COLORS
                for side in ALL_CASTLING_SIDES
                if CastlingRight(color=color, side=side) in rights.available
            ]
        )
