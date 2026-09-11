"""
What a game status implies.
"""

from idl.chess.model.game_pb2 import (
    GAME_STATUS_CHECK,
    GAME_STATUS_DRAW_BY_FIFTY_MOVE_RULE,
    GAME_STATUS_DRAW_BY_INSUFFICIENT_MATERIAL,
    GAME_STATUS_DRAW_BY_REPETITION,
    GAME_STATUS_IN_PROGRESS,
    GAME_STATUS_STALEMATE,
    GameStatus,
)

CONTINUING_STATUSES: tuple[GameStatus, ...] = (GAME_STATUS_IN_PROGRESS, GAME_STATUS_CHECK)
DRAWN_STATUSES: tuple[GameStatus, ...] = (
    GAME_STATUS_STALEMATE,
    GAME_STATUS_DRAW_BY_FIFTY_MOVE_RULE,
    GAME_STATUS_DRAW_BY_REPETITION,
    GAME_STATUS_DRAW_BY_INSUFFICIENT_MATERIAL,
)


class GameStatuses:
    """
    What is true of a game status.
    """

    @staticmethod
    def is_terminal(status: GameStatus) -> bool:
        return status not in CONTINUING_STATUSES

    @staticmethod
    def is_draw(status: GameStatus) -> bool:
        return status in DRAWN_STATUSES
