from dataclasses import dataclass

from chess.models.castling_side import CastlingSide
from chess.models.color import Color


@dataclass(frozen=True, slots=True)
class CastlingRight:
    """
    One side's claim to one of its two castles.
    """

    color: Color
    side: CastlingSide
