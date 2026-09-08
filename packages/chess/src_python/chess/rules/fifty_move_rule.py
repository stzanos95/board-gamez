"""
The fifty-move rule.

Fifty moves by each player without a capture or a pawn move. The halfmove clock
counts single-player moves, so the limit is twice that.
"""

from chess.board.chess_board_state import ChessBoardState

MOVES_WITHOUT_PROGRESS_LIMIT = 50
PLAYERS_PER_MOVE = 2
MAX_HALFMOVE_CLOCK = MOVES_WITHOUT_PROGRESS_LIMIT * PLAYERS_PER_MOVE


class FiftyMoveRule:
    """
    Draw because neither side has made progress for fifty moves.
    """

    @staticmethod
    def is_draw(state: ChessBoardState) -> bool:
        """
        Whether the halfmove clock has reached the limit.

        The state's clock resets on a capture or a pawn move, so reaching the
        limit means neither has happened for fifty moves by each player.
        """
        return state.halfmove_clock >= MAX_HALFMOVE_CLOCK
