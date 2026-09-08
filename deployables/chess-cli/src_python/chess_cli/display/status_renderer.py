"""
Saying in words where the game stands.
"""

from chess.engine.chess_engine import ChessEngine
from chess.models.game_result import GameResult
from chess.models.game_status import GameStatus

DRAW_DESCRIPTIONS_BY_STATUS: dict[GameStatus, str] = {
    GameStatus.STALEMATE: "stalemate",
    GameStatus.DRAW_BY_FIFTY_MOVE_RULE: "the fifty-move rule",
    GameStatus.DRAW_BY_REPETITION: "threefold repetition",
    GameStatus.DRAW_BY_INSUFFICIENT_MATERIAL: "insufficient material",
}
UNKNOWN_DRAW_DESCRIPTION = "agreement"


class StatusRenderer:
    """
    Putting the state of a game into a sentence.
    """

    @staticmethod
    def render_status(engine: ChessEngine) -> str:
        """
        Where the game stands, or an empty string when there is nothing to say.
        """
        result = engine.result
        if result is not None:
            return StatusRenderer.render_result(result)
        if engine.status is GameStatus.CHECK:
            return f"{engine.active_player.name} is in check."
        return ""

    @staticmethod
    def render_result(result: GameResult) -> str:
        """
        How the game finished, naming the winner and the scoreline.
        """
        if result.resigning_player is not None and result.winner is not None:
            return (
                f"{result.resigning_player.name} resigns. "
                f"{result.winner.name} wins. {result.outcome.scoreline}"
            )
        if result.winner is not None:
            return f"Checkmate. {result.winner.name} wins. {result.outcome.scoreline}"
        description = (
            UNKNOWN_DRAW_DESCRIPTION
            if result.status is None
            else DRAW_DESCRIPTIONS_BY_STATUS.get(result.status, UNKNOWN_DRAW_DESCRIPTION)
        )
        return f"Draw by {description}. {result.outcome.scoreline}"
