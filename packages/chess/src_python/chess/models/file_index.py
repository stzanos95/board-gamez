from enum import Enum

from chess.core.errors import NotationError

FILE_LETTERS = "abcdefgh"


class File(Enum):
    """
    A column of the board, indexed from zero at the queenside edge.
    """

    A = 0
    B = 1
    C = 2
    D = 3
    E = 4
    F = 5
    G = 6
    H = 7

    @property
    def letter(self) -> str:
        return FILE_LETTERS[self.value]

    @staticmethod
    def from_letter(letter: str) -> "File":
        if letter not in FILE_LETTERS:
            raise NotationError(f"got file {letter!r}, expected one of {FILE_LETTERS!r}")
        return File(FILE_LETTERS.index(letter))
