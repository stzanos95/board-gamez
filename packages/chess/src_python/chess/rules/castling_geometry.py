"""
The fixed geometry of the four castles.

Each entry names the king and rook squares, the squares that must be vacant, and
the squares the enemy must not attack.

Those two lists differ queenside: the b-file square must be vacant but may be
attacked, because the king does not stand on it.
"""

from dataclasses import dataclass

from idl.chess.model.castling_pb2 import (
    CASTLING_SIDE_KINGSIDE,
    CASTLING_SIDE_QUEENSIDE,
    CastlingRight,
)
from idl.chess.model.piece_pb2 import COLOR_BLACK, COLOR_WHITE, Color
from idl.chess.model.square_pb2 import Square

from chess.core.squares import Squares


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
    right=CastlingRight(color=COLOR_WHITE, side=CASTLING_SIDE_KINGSIDE),
    king_origin=Squares.from_algebraic("e1"),
    king_destination=Squares.from_algebraic("g1"),
    rook_origin=Squares.from_algebraic("h1"),
    rook_destination=Squares.from_algebraic("f1"),
    vacant_squares=(Squares.from_algebraic("f1"), Squares.from_algebraic("g1")),
    unattacked_squares=(
        Squares.from_algebraic("e1"),
        Squares.from_algebraic("f1"),
        Squares.from_algebraic("g1"),
    ),
)

WHITE_QUEENSIDE_CASTLING = CastlingGeometry(
    right=CastlingRight(color=COLOR_WHITE, side=CASTLING_SIDE_QUEENSIDE),
    king_origin=Squares.from_algebraic("e1"),
    king_destination=Squares.from_algebraic("c1"),
    rook_origin=Squares.from_algebraic("a1"),
    rook_destination=Squares.from_algebraic("d1"),
    vacant_squares=(
        Squares.from_algebraic("b1"),
        Squares.from_algebraic("c1"),
        Squares.from_algebraic("d1"),
    ),
    unattacked_squares=(
        Squares.from_algebraic("e1"),
        Squares.from_algebraic("d1"),
        Squares.from_algebraic("c1"),
    ),
)

BLACK_KINGSIDE_CASTLING = CastlingGeometry(
    right=CastlingRight(color=COLOR_BLACK, side=CASTLING_SIDE_KINGSIDE),
    king_origin=Squares.from_algebraic("e8"),
    king_destination=Squares.from_algebraic("g8"),
    rook_origin=Squares.from_algebraic("h8"),
    rook_destination=Squares.from_algebraic("f8"),
    vacant_squares=(Squares.from_algebraic("f8"), Squares.from_algebraic("g8")),
    unattacked_squares=(
        Squares.from_algebraic("e8"),
        Squares.from_algebraic("f8"),
        Squares.from_algebraic("g8"),
    ),
)

BLACK_QUEENSIDE_CASTLING = CastlingGeometry(
    right=CastlingRight(color=COLOR_BLACK, side=CASTLING_SIDE_QUEENSIDE),
    king_origin=Squares.from_algebraic("e8"),
    king_destination=Squares.from_algebraic("c8"),
    rook_origin=Squares.from_algebraic("a8"),
    rook_destination=Squares.from_algebraic("d8"),
    vacant_squares=(
        Squares.from_algebraic("b8"),
        Squares.from_algebraic("c8"),
        Squares.from_algebraic("d8"),
    ),
    unattacked_squares=(
        Squares.from_algebraic("e8"),
        Squares.from_algebraic("d8"),
        Squares.from_algebraic("c8"),
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
            geometry for geometry in ALL_CASTLING_GEOMETRIES if geometry.right.color == color
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
