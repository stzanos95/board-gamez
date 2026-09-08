from dataclasses import dataclass

from chess.models.algebraic_move_text import AlgebraicMoveText
from chess.models.chess_player import ChessPlayer
from chess.models.game_status import GameStatus
from chess.models.move import Move


@dataclass(frozen=True, slots=True)
class ChessTurn:
    """
    One move that was played, with its written form.

    The notation is stored because rendering it needs the position the move was
    played from, which is unavailable when the history is read. It is a named
    type so it cannot be confused with coordinate text.
    """

    number: int
    player: ChessPlayer
    move: Move
    notation: AlgebraicMoveText
    resulting_status: GameStatus
