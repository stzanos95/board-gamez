"""
The eight L-shaped displacements a knight leaps.
"""

from chess.models.vector import Vector

KNIGHT_OFFSETS: tuple[Vector, ...] = (
    Vector(file_delta=1, rank_delta=2),
    Vector(file_delta=2, rank_delta=1),
    Vector(file_delta=2, rank_delta=-1),
    Vector(file_delta=1, rank_delta=-2),
    Vector(file_delta=-1, rank_delta=-2),
    Vector(file_delta=-2, rank_delta=-1),
    Vector(file_delta=-2, rank_delta=1),
    Vector(file_delta=-1, rank_delta=2),
)
