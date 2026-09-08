from dataclasses import dataclass

from chess.core.board_dimensions import (
    FILE_COUNT,
    FIRST_FILE_INDEX,
    FIRST_RANK_INDEX,
    RANK_COUNT,
)
from chess.core.errors import NotationError
from chess.models.file_index import File
from chess.models.rank_index import Rank
from chess.models.vector import Vector

ALGEBRAIC_LENGTH = 2
LIGHT_SQUARE_PARITY = 1


@dataclass(frozen=True, slots=True)
class Square:
    """
    One of the sixty-four squares, named by its file and rank.
    """

    file: File
    rank: Rank

    @property
    def algebraic(self) -> str:
        return f"{self.file.letter}{self.rank.digit}"

    @property
    def is_light(self) -> bool:
        # A bishop never leaves its starting square colour. King and bishop against
        # king and bishop is a draw only when both bishops travel on one colour.
        return (self.file.value + self.rank.value) % 2 == LIGHT_SQUARE_PARITY

    def shifted(self, vector: Vector) -> "Square | None":
        """
        The square this displacement lands on, or None if it leaves the board.
        """
        file_index = self.file.value + vector.file_delta
        rank_index = self.rank.value + vector.rank_delta
        if not FIRST_FILE_INDEX <= file_index < FILE_COUNT:
            return None
        if not FIRST_RANK_INDEX <= rank_index < RANK_COUNT:
            return None
        return Square(file=File(file_index), rank=Rank(rank_index))

    @staticmethod
    def from_algebraic(text: str) -> "Square":
        if len(text) != ALGEBRAIC_LENGTH:
            raise NotationError(f"got square {text!r}, expected two characters such as 'e4'")
        return Square(file=File.from_letter(text[0]), rank=Rank.from_digit(text[1]))
