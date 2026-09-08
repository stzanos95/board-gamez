from enum import Enum

from chess.models.vector import Vector


class Direction(Enum):
    """
    The eight compass directions a queen may travel.

    Named from White's point of view: NORTH increases the rank.
    """

    _value_: Vector

    NORTH = Vector(file_delta=0, rank_delta=1)
    NORTH_EAST = Vector(file_delta=1, rank_delta=1)
    EAST = Vector(file_delta=1, rank_delta=0)
    SOUTH_EAST = Vector(file_delta=1, rank_delta=-1)
    SOUTH = Vector(file_delta=0, rank_delta=-1)
    SOUTH_WEST = Vector(file_delta=-1, rank_delta=-1)
    WEST = Vector(file_delta=-1, rank_delta=0)
    NORTH_WEST = Vector(file_delta=-1, rank_delta=1)

    @property
    def vector(self) -> Vector:
        return self._value_
