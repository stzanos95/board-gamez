"""
Everything about a pawn that depends on its colour.

A pawn is the only piece whose geometry differs between the two sides, so each of
these is a lookup on colour rather than a constant.
"""

from chess.models.color import Color
from chess.models.direction import Direction
from chess.models.piece_type import PieceType
from chess.models.rank_index import Rank

# Order matters only for presentation: a queen is what a player almost always
# wants, so it is offered first.
PAWN_PROMOTION_TYPES: tuple[PieceType, ...] = (
    PieceType.QUEEN,
    PieceType.ROOK,
    PieceType.BISHOP,
    PieceType.KNIGHT,
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
        return Direction.NORTH if color is Color.WHITE else Direction.SOUTH

    @staticmethod
    def start_rank(color: Color) -> Rank:
        """
        The rank this colour's pawns begin on, and the only one they may double
        push from.
        """
        return Rank.TWO if color is Color.WHITE else Rank.SEVEN

    @staticmethod
    def promotion_rank(color: Color) -> Rank:
        """
        The rank on which this colour's pawns must become another piece.
        """
        return Rank.EIGHT if color is Color.WHITE else Rank.ONE

    @staticmethod
    def capture_directions(color: Color) -> tuple[Direction, ...]:
        """
        The two diagonals this colour's pawns capture along.
        """
        if color is Color.WHITE:
            return (Direction.NORTH_WEST, Direction.NORTH_EAST)
        return (Direction.SOUTH_WEST, Direction.SOUTH_EAST)
