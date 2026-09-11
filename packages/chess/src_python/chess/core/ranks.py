"""
The rows of the board, and the digits they are written with.
"""

from idl.chess.model.square_pb2 import (
    RANK_1,
    RANK_2,
    RANK_3,
    RANK_4,
    RANK_5,
    RANK_6,
    RANK_7,
    RANK_8,
    Rank,
)

from chess.core.board_dimensions import FIRST_RANK_NUMBER
from chess.core.errors import NotationError

RANK_DIGITS = "12345678"

ALL_RANKS: tuple[Rank, ...] = (RANK_1, RANK_2, RANK_3, RANK_4, RANK_5, RANK_6, RANK_7, RANK_8)


class Ranks:
    """
    Reading and writing a rank.
    """

    @staticmethod
    def digit(rank: Rank) -> str:
        return RANK_DIGITS[rank - FIRST_RANK_NUMBER]

    @staticmethod
    def from_digit(digit: str) -> Rank:
        if digit not in RANK_DIGITS:
            raise NotationError(f"got rank {digit!r}, expected one of {RANK_DIGITS!r}")
        return ALL_RANKS[RANK_DIGITS.index(digit)]

    @staticmethod
    def from_number(number: int) -> Rank | None:
        """
        The rank with this number, or None when it is off the board.
        """
        if not FIRST_RANK_NUMBER <= number < FIRST_RANK_NUMBER + len(ALL_RANKS):
            return None
        return ALL_RANKS[number - FIRST_RANK_NUMBER]
