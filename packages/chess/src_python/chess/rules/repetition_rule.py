"""
Draw by threefold repetition.
"""

from idl.chess.model.board_pb2 import PositionKey

REPETITION_LIMIT = 3


class RepetitionRule:
    """
    Draw because the same position has been reached three times.
    """

    @staticmethod
    def is_draw(position_keys: tuple[PositionKey, ...]) -> bool:
        """
        Whether the position now on the board has appeared three times.

        Takes every position the game has passed through, most recent last, and
        counts how often the last of them occurs.
        """
        if not position_keys:
            return False
        return position_keys.count(position_keys[-1]) >= REPETITION_LIMIT
