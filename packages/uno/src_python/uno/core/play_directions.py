"""
The two ways play goes round.
"""

from idl.uno.model.game_pb2 import (
    PLAY_DIRECTION_CLOCKWISE,
    PLAY_DIRECTION_COUNTERCLOCKWISE,
    PlayDirection,
)

CLOCKWISE_STEP = 1
COUNTERCLOCKWISE_STEP = -1


class PlayDirections:
    """
    What is true of a direction.
    """

    @staticmethod
    def reversed(direction: PlayDirection) -> PlayDirection:
        return (
            PLAY_DIRECTION_COUNTERCLOCKWISE
            if direction == PLAY_DIRECTION_CLOCKWISE
            else PLAY_DIRECTION_CLOCKWISE
        )

    @staticmethod
    def step(direction: PlayDirection) -> int:
        """
        How far along the turn order one move in this direction goes.
        """
        return CLOCKWISE_STEP if direction == PLAY_DIRECTION_CLOCKWISE else COUNTERCLOCKWISE_STEP
