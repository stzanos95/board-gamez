"""
The direction bundles each sliding piece travels along.
"""

from chess.models.direction import Direction

ORTHOGONAL_DIRECTIONS: tuple[Direction, ...] = (
    Direction.NORTH,
    Direction.EAST,
    Direction.SOUTH,
    Direction.WEST,
)

DIAGONAL_DIRECTIONS: tuple[Direction, ...] = (
    Direction.NORTH_EAST,
    Direction.SOUTH_EAST,
    Direction.SOUTH_WEST,
    Direction.NORTH_WEST,
)

ALL_EIGHT_DIRECTIONS: tuple[Direction, ...] = ORTHOGONAL_DIRECTIONS + DIAGONAL_DIRECTIONS
