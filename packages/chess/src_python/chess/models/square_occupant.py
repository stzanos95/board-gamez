from dataclasses import dataclass

from chess.models.occupant import Occupant
from chess.models.square import Square


@dataclass(frozen=True, slots=True)
class SquareOccupant:
    """
    One square and the piece standing on it.

    Lets a whole position be summarised as a set.
    """

    square: Square
    occupant: Occupant
