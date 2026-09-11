"""
The scoresheet: "1. e4 e5 2. Bc4 Nc6 ...".
"""

import textwrap

from idl.chess.model import piece_pb2
from idl.chess.model.game_pb2 import ChessTurn

MOVE_LIST_WIDTH = 72
BLACK_FIRST_MARKER = "..."


class MoveListRenderer:
    """
    Writing the moves played as a scoresheet reads them.
    """

    @staticmethod
    def render(turns: tuple[ChessTurn, ...]) -> str:
        """
        The moves so far, numbered in pairs and wrapped to a readable width.

        Empty when nothing has been played.
        """
        if not turns:
            return ""
        numbered: list[str] = []
        for turn in turns:
            if turn.player.color == piece_pb2.COLOR_WHITE:
                numbered.append(f"{turn.number}. {turn.notation}")
            elif numbered:
                numbered[-1] = f"{numbered[-1]} {turn.notation}"
            else:
                # Only reachable from a position where Black moves first.
                numbered.append(f"{turn.number}{BLACK_FIRST_MARKER} {turn.notation}")
        return textwrap.fill(" ".join(numbered), width=MOVE_LIST_WIDTH)
