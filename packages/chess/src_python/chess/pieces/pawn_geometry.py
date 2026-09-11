"""
Everything about a pawn that depends on its colour.

A pawn is the only piece whose geometry differs between the two sides, so each of
these is a lookup on colour rather than a constant.
"""

from idl.chess.model.piece_pb2 import (
    COLOR_WHITE,
    PIECE_TYPE_BISHOP,
    PIECE_TYPE_KNIGHT,
    PIECE_TYPE_QUEEN,
    PIECE_TYPE_ROOK,
    Color,
    PieceType,
)
from idl.chess.model.square_pb2 import RANK_1, RANK_2, RANK_7, RANK_8, Rank

from chess.movement.direction import Direction

# Order matters only for presentation: a queen is what a player almost always
# wants, so it is offered first.
PAWN_PROMOTION_TYPES: tuple[PieceType, ...] = (
    PIECE_TYPE_QUEEN,
    PIECE_TYPE_ROOK,
    PIECE_TYPE_BISHOP,
    PIECE_TYPE_KNIGHT,
)


class PawnGeometry:
    """
    The colour-dependent facts about how a pawn travels.
    """

    @staticmethod
    def forward_direction(color: Color) -> Direction:
        """
        The one direction this colour's pawns advance in.
        """
        return Direction.NORTH if color == COLOR_WHITE else Direction.SOUTH

    @staticmethod
    def start_rank(color: Color) -> Rank:
        """
        The rank this colour's pawns begin on, and the only one they may double
        push from.
        """
        return RANK_2 if color == COLOR_WHITE else RANK_7

    @staticmethod
    def promotion_rank(color: Color) -> Rank:
        """
        The rank on which this colour's pawns must become another piece.
        """
        return RANK_8 if color == COLOR_WHITE else RANK_1

    @staticmethod
    def capture_directions(color: Color) -> tuple[Direction, ...]:
        """
        The two diagonals this colour's pawns capture along.
        """
        if color == COLOR_WHITE:
            return (Direction.NORTH_WEST, Direction.NORTH_EAST)
        return (Direction.SOUTH_WEST, Direction.SOUTH_EAST)
