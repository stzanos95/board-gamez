from dataclasses import dataclass

from chess.models.chess_player import ChessPlayer
from chess.models.game_outcome import GameOutcome
from chess.models.game_status import GameStatus


@dataclass(frozen=True, slots=True)
class GameResult:
    """
    How a game finished.

    Exactly one of `status` and `resigning_player` is set. A game decided on the
    board carries the status that ended it; a game decided by resignation carries
    the player who resigned.
    """

    outcome: GameOutcome
    winner: ChessPlayer | None
    status: GameStatus | None
    resigning_player: ChessPlayer | None
