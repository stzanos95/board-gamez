from enum import Enum


class GameStatus(Enum):
    """
    Where a game stands after the move just played.
    """

    IN_PROGRESS = "in_progress"
    CHECK = "check"
    CHECKMATE = "checkmate"
    STALEMATE = "stalemate"
    DRAW_BY_FIFTY_MOVE_RULE = "draw_by_fifty_move_rule"
    DRAW_BY_REPETITION = "draw_by_repetition"
    DRAW_BY_INSUFFICIENT_MATERIAL = "draw_by_insufficient_material"

    @property
    def is_terminal(self) -> bool:
        return self is not GameStatus.IN_PROGRESS and self is not GameStatus.CHECK

    @property
    def is_draw(self) -> bool:
        return self in (
            GameStatus.STALEMATE,
            GameStatus.DRAW_BY_FIFTY_MOVE_RULE,
            GameStatus.DRAW_BY_REPETITION,
            GameStatus.DRAW_BY_INSUFFICIENT_MATERIAL,
        )
