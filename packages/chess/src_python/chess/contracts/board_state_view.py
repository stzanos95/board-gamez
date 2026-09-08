from abc import ABC, abstractmethod

from chess.models.castling_rights import CastlingRights
from chess.models.color import Color
from chess.models.occupant import Occupant
from chess.models.square import Square


class BoardStateView(ABC):
    """
    The read-only face of a board. A piece is handed this, never the board.

    Move generation can read occupancy through it and cannot write, and `models`
    carries no dependency on `pieces`.

    Every member is a method rather than a property. An abstract property is
    inherited as a class attribute, and a dataclass field of the same name would
    take that property object as its default.
    """

    @abstractmethod
    def occupant(self, square: Square) -> Occupant | None:
        """
        Whose piece stands here and what type, or None if the square is bare.
        """

    @abstractmethod
    def is_empty(self, square: Square) -> bool: ...

    @abstractmethod
    def holds_enemy_of(self, square: Square, color: Color) -> bool: ...

    @abstractmethod
    def holds_ally_of(self, square: Square, color: Color) -> bool: ...

    @abstractmethod
    def en_passant_target_square(self) -> Square | None:
        """
        The square a pawn may capture onto this move, set by a double push.
        """

    @abstractmethod
    def available_castling_rights(self) -> CastlingRights: ...
