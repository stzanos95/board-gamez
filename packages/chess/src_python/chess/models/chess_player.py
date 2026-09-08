from dataclasses import dataclass

from chess.models.color import Color


@dataclass(frozen=True, slots=True)
class ChessPlayer:
    """
    Who is playing, and which side they have.
    """

    name: str
    color: Color
