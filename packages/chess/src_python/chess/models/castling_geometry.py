"""
The fixed geometry of the four castles.

Each entry names the king and rook squares, the squares that must be vacant, and
the squares the enemy must not attack.

Those two lists differ queenside: the b-file square must be vacant but may be
attacked, because the king does not stand on it.
"""

from dataclasses import dataclass

from chess.models.castling_right import CastlingRight
from chess.models.castling_side import CastlingSide
from chess.models.color import Color
from chess.models.square import Square


@dataclass(frozen=True, slots=True)
class CastlingGeometry:
    """
    Where everything starts and ends for one castle, and what must be true.
    """

    right: CastlingRight
    king_origin: Square
    king_destination: Square
    rook_origin: Square
    rook_destination: Square
    vacant_squares: tuple[Square, ...]
    unattacked_squares: tuple[Square, ...]


WHITE_KINGSIDE_CASTLING = CastlingGeometry(
    right=CastlingRight(color=Color.WHITE, side=CastlingSide.KINGSIDE),
    king_origin=Square.from_algebraic("e1"),
    king_destination=Square.from_algebraic("g1"),
    rook_origin=Square.from_algebraic("h1"),
    rook_destination=Square.from_algebraic("f1"),
    vacant_squares=(Square.from_algebraic("f1"), Square.from_algebraic("g1")),
    unattacked_squares=(
        Square.from_algebraic("e1"),
        Square.from_algebraic("f1"),
        Square.from_algebraic("g1"),
    ),
)

WHITE_QUEENSIDE_CASTLING = CastlingGeometry(
    right=CastlingRight(color=Color.WHITE, side=CastlingSide.QUEENSIDE),
    king_origin=Square.from_algebraic("e1"),
    king_destination=Square.from_algebraic("c1"),
    rook_origin=Square.from_algebraic("a1"),
    rook_destination=Square.from_algebraic("d1"),
    vacant_squares=(
        Square.from_algebraic("b1"),
        Square.from_algebraic("c1"),
        Square.from_algebraic("d1"),
    ),
    unattacked_squares=(
        Square.from_algebraic("e1"),
        Square.from_algebraic("d1"),
        Square.from_algebraic("c1"),
    ),
)

BLACK_KINGSIDE_CASTLING = CastlingGeometry(
    right=CastlingRight(color=Color.BLACK, side=CastlingSide.KINGSIDE),
    king_origin=Square.from_algebraic("e8"),
    king_destination=Square.from_algebraic("g8"),
    rook_origin=Square.from_algebraic("h8"),
    rook_destination=Square.from_algebraic("f8"),
    vacant_squares=(Square.from_algebraic("f8"), Square.from_algebraic("g8")),
    unattacked_squares=(
        Square.from_algebraic("e8"),
        Square.from_algebraic("f8"),
        Square.from_algebraic("g8"),
    ),
)

BLACK_QUEENSIDE_CASTLING = CastlingGeometry(
    right=CastlingRight(color=Color.BLACK, side=CastlingSide.QUEENSIDE),
    king_origin=Square.from_algebraic("e8"),
    king_destination=Square.from_algebraic("c8"),
    rook_origin=Square.from_algebraic("a8"),
    rook_destination=Square.from_algebraic("d8"),
    vacant_squares=(
        Square.from_algebraic("b8"),
        Square.from_algebraic("c8"),
        Square.from_algebraic("d8"),
    ),
    unattacked_squares=(
        Square.from_algebraic("e8"),
        Square.from_algebraic("d8"),
        Square.from_algebraic("c8"),
    ),
)

ALL_CASTLING_GEOMETRIES: tuple[CastlingGeometry, ...] = (
    WHITE_KINGSIDE_CASTLING,
    WHITE_QUEENSIDE_CASTLING,
    BLACK_KINGSIDE_CASTLING,
    BLACK_QUEENSIDE_CASTLING,
)


class CastlingGeometryLookup:
    """
    Finding the fixed geometry that applies to a colour or a square.
    """

    @staticmethod
    def geometries_for_color(color: Color) -> tuple[CastlingGeometry, ...]:
        """
        Both castles available to this colour, kingside first.
        """
        return tuple(
            geometry for geometry in ALL_CASTLING_GEOMETRIES if geometry.right.color is color
        )

    @staticmethod
    def right_anchored_at_square(square: Square) -> CastlingRight | None:
        """
        The right lost when this square is vacated or captured on, or None if no
        right depends on it.

        Covers the four rook corners. A king that moves forfeits both of its
        castles, which callers handle by colour instead.
        """
        for geometry in ALL_CASTLING_GEOMETRIES:
            if geometry.rook_origin == square:
                return geometry.right
        return None
