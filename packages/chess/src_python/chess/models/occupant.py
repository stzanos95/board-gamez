from dataclasses import dataclass

from chess.models.color import Color
from chess.models.piece_type import PieceType


@dataclass(frozen=True, slots=True)
class Occupant:
    """
    Whose piece stands on a square, and what type.

    A BoardStateView returns this instead of a piece object. Move generation needs
    only the colour and the type.
    """

    color: Color
    piece_type: PieceType
