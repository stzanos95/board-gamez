from dataclasses import dataclass

from chess.models.chess_turn import ChessTurn
from chess.models.position_key import PositionKey


@dataclass(frozen=True, slots=True)
class ChessTurnHistory:
    """
    The turns played, and the position after each of them.

    The keys run one ahead of the turns: the opening position counts as visited
    before either player has moved.
    """

    turns: tuple[ChessTurn, ...]
    position_keys: tuple[PositionKey, ...]

    @staticmethod
    def opening(initial_position_key: PositionKey) -> "ChessTurnHistory":
        return ChessTurnHistory(turns=(), position_keys=(initial_position_key,))

    def extended(self, turn: ChessTurn, position_key: PositionKey) -> "ChessTurnHistory":
        return ChessTurnHistory(
            turns=(*self.turns, turn),
            position_keys=(*self.position_keys, position_key),
        )
