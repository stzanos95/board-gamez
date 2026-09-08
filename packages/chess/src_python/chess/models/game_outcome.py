from enum import Enum

from chess.models.color import Color


class GameOutcome(Enum):
    """
    How a finished game is scored. The values are the standard scorelines.
    """

    WHITE_WINS = "1-0"
    BLACK_WINS = "0-1"
    DRAW = "1/2-1/2"

    @property
    def scoreline(self) -> str:
        return self.value

    @staticmethod
    def for_winner(color: Color) -> "GameOutcome":
        """
        The outcome in which this colour is the winner.
        """
        return GameOutcome.WHITE_WINS if color is Color.WHITE else GameOutcome.BLACK_WINS
