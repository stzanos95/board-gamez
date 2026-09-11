"""
Saying in words where the game stands.
"""

from chess.engine.chess_engine import ChessEngine
from idl.chess.model import game_pb2
from idl.chess.model.game_pb2 import GameResult

from chess_cli.player_names import PlayerNames

DrawDescriptionsByStatus = dict[game_pb2.GameStatus, str]
ScorelinesByOutcome = dict[game_pb2.GameOutcome, str]

DRAW_DESCRIPTIONS_BY_STATUS: DrawDescriptionsByStatus = {
    game_pb2.GAME_STATUS_STALEMATE: "stalemate",
    game_pb2.GAME_STATUS_DRAW_BY_FIFTY_MOVE_RULE: "the fifty-move rule",
    game_pb2.GAME_STATUS_DRAW_BY_REPETITION: "threefold repetition",
    game_pb2.GAME_STATUS_DRAW_BY_INSUFFICIENT_MATERIAL: "insufficient material",
}
UNKNOWN_DRAW_DESCRIPTION = "agreement"

SCORELINES_BY_OUTCOME: ScorelinesByOutcome = {
    game_pb2.GAME_OUTCOME_WHITE_WINS: "1-0",
    game_pb2.GAME_OUTCOME_BLACK_WINS: "0-1",
    game_pb2.GAME_OUTCOME_DRAW: "1/2-1/2",
}


class StatusRenderer:
    """
    Putting the state of a game into a sentence.
    """

    @staticmethod
    def render_status(engine: ChessEngine, names: PlayerNames) -> str:
        """
        Where the game stands, or an empty string when there is nothing to say.
        """
        result = engine.result
        if result is not None:
            return StatusRenderer.render_result(result, names)
        if engine.status == game_pb2.GAME_STATUS_CHECK:
            return f"{names.get_name(engine.active_player)} is in check."
        return ""

    @staticmethod
    def render_result(result: GameResult, names: PlayerNames) -> str:
        """
        How the game finished, naming the winner and the scoreline.
        """
        scoreline = SCORELINES_BY_OUTCOME[result.outcome]
        if result.HasField("resigning_player") and result.HasField("winner"):
            return (
                f"{names.get_name(result.resigning_player)} resigns. "
                f"{names.get_name(result.winner)} wins. {scoreline}"
            )
        if result.HasField("winner"):
            return f"Checkmate. {names.get_name(result.winner)} wins. {scoreline}"
        description = DRAW_DESCRIPTIONS_BY_STATUS.get(result.status, UNKNOWN_DRAW_DESCRIPTION)
        return f"Draw by {description}. {scoreline}"
