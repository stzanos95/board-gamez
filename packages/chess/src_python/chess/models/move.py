from dataclasses import dataclass

from chess.models.castling_side import CastlingSide
from chess.models.color import Color
from chess.models.move_type import MoveType
from chess.models.piece_type import PieceType
from chess.models.square import Square


@dataclass(frozen=True, slots=True)
class Move:
    """
    One move, complete enough for a board to apply without deriving anything.

    The mover is carried as colour and type rather than as a piece object.

    `captured_square` differs from `destination` for en passant. The rook fields
    are set only for a castle.
    """

    origin: Square
    destination: Square
    moving_color: Color
    moving_piece_type: PieceType
    move_type: MoveType
    captured_square: Square | None = None
    promotion_type: PieceType | None = None
    castling_side: CastlingSide | None = None
    rook_origin: Square | None = None
    rook_destination: Square | None = None
