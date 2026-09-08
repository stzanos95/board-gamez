from dataclasses import dataclass

from chess.core.errors import ChessError
from chess.models.chess_player import ChessPlayer
from chess.models.color import Color


@dataclass(frozen=True, slots=True)
class PlayerRoster:
    """
    The two players, addressable by colour.

    Named fields rather than a pair, so the sides cannot be passed the wrong way
    round.
    """

    white: ChessPlayer
    black: ChessPlayer

    def __post_init__(self) -> None:
        if self.white.color is not Color.WHITE:
            raise ChessError(f"{self.white.name} was seated as White but holds {self.white.color}")
        if self.black.color is not Color.BLACK:
            raise ChessError(f"{self.black.name} was seated as Black but holds {self.black.color}")

    def player_for(self, color: Color) -> ChessPlayer:
        return self.white if color is Color.WHITE else self.black
