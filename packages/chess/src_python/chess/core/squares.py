"""
The sixty-four squares: naming them, indexing them, and moving between them.

A square is the schema's message and carries no identity of its own, so a board
keyed by square uses the index this module computes.
"""

from idl.chess.model.square_pb2 import Square

from chess.core.board_dimensions import FILE_COUNT, FIRST_FILE_NUMBER, FIRST_RANK_NUMBER
from chess.core.errors import NotationError
from chess.core.files import Files
from chess.core.ranks import Ranks
from chess.movement.vector import Vector

ALGEBRAIC_LENGTH = 2
LIGHT_SQUARE_PARITY = 1

SquareIndex = int


class Squares:
    """
    What is true of a square, and how it is written.
    """

    @staticmethod
    def get_index(square: Square) -> SquareIndex:
        """
        The square's place in a rank-major grid, 0 for a1 and 63 for h8.
        """
        return (square.rank - FIRST_RANK_NUMBER) * FILE_COUNT + (square.file - FIRST_FILE_NUMBER)

    @staticmethod
    def algebraic(square: Square) -> str:
        return f"{Files.letter(square.file)}{Ranks.digit(square.rank)}"

    @staticmethod
    def from_algebraic(text: str) -> Square:
        if len(text) != ALGEBRAIC_LENGTH:
            raise NotationError(f"got square {text!r}, expected two characters such as 'e4'")
        return Square(file=Files.from_letter(text[0]), rank=Ranks.from_digit(text[1]))

    @staticmethod
    def is_light(square: Square) -> bool:
        # A bishop never leaves its starting square colour. King and bishop against
        # king and bishop is a draw only when both bishops travel on one colour.
        return (square.file + square.rank) % 2 == LIGHT_SQUARE_PARITY

    @staticmethod
    def shifted(square: Square, vector: Vector) -> Square | None:
        """
        The square this displacement lands on, or None if it leaves the board.
        """
        file = Files.from_number(square.file + vector.file_delta)
        rank = Ranks.from_number(square.rank + vector.rank_delta)
        if file is None or rank is None:
            return None
        return Square(file=file, rank=rank)
