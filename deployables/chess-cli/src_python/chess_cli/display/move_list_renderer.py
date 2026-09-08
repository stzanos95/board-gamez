"""
The scoresheet: "1. e4 e5 2. Bc4 Nc6 ...".
"""

import textwrap

from chess.models.chess_turn_history import ChessTurnHistory
from chess.models.color import Color

MOVE_LIST_WIDTH = 72
BLACK_FIRST_MARKER = "..."


class MoveListRenderer:
    """
    Writing the moves played as a scoresheet reads them.
    """

    @staticmethod
    def render(history: ChessTurnHistory) -> str:
        """
        The moves so far, numbered in pairs and wrapped to a readable width.

        Empty when nothing has been played.
        """
        if not history.turns:
            return ""
        numbered: list[str] = []
        for turn in history.turns:
            if turn.player.color is Color.WHITE:
                numbered.append(f"{turn.number}. {turn.notation.text}")
            elif numbered:
                numbered[-1] = f"{numbered[-1]} {turn.notation.text}"
            else:
                # Only reachable from a position where Black moves first.
                numbered.append(f"{turn.number}{BLACK_FIRST_MARKER} {turn.notation.text}")
        return textwrap.fill(" ".join(numbered), width=MOVE_LIST_WIDTH)
