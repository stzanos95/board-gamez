from enum import Enum

from chess.core.board_dimensions import RANK_LABEL_OFFSET
from chess.core.errors import NotationError

RANK_DIGITS = "12345678"


class Rank(Enum):
    """
    A row of the board, indexed from zero at White's back rank.
    """

    ONE = 0
    TWO = 1
    THREE = 2
    FOUR = 3
    FIVE = 4
    SIX = 5
    SEVEN = 6
    EIGHT = 7

    @property
    def digit(self) -> str:
        return str(self.value + RANK_LABEL_OFFSET)

    @staticmethod
    def from_digit(digit: str) -> "Rank":
        if digit not in RANK_DIGITS:
            raise NotationError(f"got rank {digit!r}, expected one of {RANK_DIGITS!r}")
        return Rank(RANK_DIGITS.index(digit))
