"""
The columns of the board, and the letters they are written with.
"""

from idl.chess.model.square_pb2 import (
    FILE_A,
    FILE_B,
    FILE_C,
    FILE_D,
    FILE_E,
    FILE_F,
    FILE_G,
    FILE_H,
    File,
)

from chess.core.board_dimensions import FIRST_FILE_NUMBER
from chess.core.errors import NotationError

FILE_LETTERS = "abcdefgh"

ALL_FILES: tuple[File, ...] = (FILE_A, FILE_B, FILE_C, FILE_D, FILE_E, FILE_F, FILE_G, FILE_H)


class Files:
    """
    Reading and writing a file.
    """

    @staticmethod
    def letter(file: File) -> str:
        return FILE_LETTERS[file - FIRST_FILE_NUMBER]

    @staticmethod
    def from_letter(letter: str) -> File:
        if letter not in FILE_LETTERS:
            raise NotationError(f"got file {letter!r}, expected one of {FILE_LETTERS!r}")
        return ALL_FILES[FILE_LETTERS.index(letter)]

    @staticmethod
    def from_number(number: int) -> File | None:
        """
        The file with this number, or None when it is off the board.
        """
        if not FIRST_FILE_NUMBER <= number < FIRST_FILE_NUMBER + len(ALL_FILES):
            return None
        return ALL_FILES[number - FIRST_FILE_NUMBER]
