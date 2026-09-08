from dataclasses import dataclass

from chess.models.piece_type import PieceType
from chess.models.square import Square


@dataclass(frozen=True, slots=True)
class ParsedCoordinateMove:
    """
    A coordinate move after parsing, before it is matched against the position.

    Named fields rather than a triple: the two squares share a type, and a
    transposition would quietly describe the move backwards.
    """

    origin: Square
    destination: Square
    promotion_type: PieceType | None
