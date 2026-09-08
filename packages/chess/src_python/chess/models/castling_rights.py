from dataclasses import dataclass

from chess.models.castling_right import CastlingRight
from chess.models.castling_side import CastlingSide
from chess.models.color import Color


@dataclass(frozen=True, slots=True)
class CastlingRights:
    """
    Which castles remain available.

    A right survives until the king or the matching rook moves, or that rook is
    captured. It does not say whether the castle is legal now: that also depends
    on occupancy and on which squares the enemy attacks.
    """

    available: frozenset[CastlingRight]

    @staticmethod
    def full() -> "CastlingRights":
        return CastlingRights(
            available=frozenset(
                CastlingRight(color=color, side=side) for color in Color for side in CastlingSide
            )
        )

    @staticmethod
    def none() -> "CastlingRights":
        return CastlingRights(available=frozenset())

    def allows(self, color: Color, side: CastlingSide) -> bool:
        return CastlingRight(color=color, side=side) in self.available

    def without(self, right: CastlingRight) -> "CastlingRights":
        return CastlingRights(available=self.available - {right})

    def without_color(self, color: Color) -> "CastlingRights":
        return CastlingRights(
            available=frozenset(right for right in self.available if right.color is not color)
        )
