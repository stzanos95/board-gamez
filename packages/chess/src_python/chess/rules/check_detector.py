"""
Whether a king stands under attack.
"""

from chess.board.chess_board_state import ChessBoardState
from chess.models.color import Color
from chess.rules.attack_map import AttackMap


class CheckDetector:
    """
    The one place check is decided.
    """

    @staticmethod
    def is_in_check(state: ChessBoardState, color: Color) -> bool:
        """
        Whether this side's king stands on a square the enemy attacks.

        Returns False when the position holds no king of that colour, so that a
        test may build a position from a handful of pieces.
        """
        king_square = state.king_square(color)
        if king_square is None:
            return False
        return AttackMap.is_square_attacked_by(
            state=state, square=king_square, color=color.opponent
        )
