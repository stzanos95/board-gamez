"""
The two sides.
"""

from idl.chess.model.piece_pb2 import COLOR_BLACK, COLOR_WHITE, Color

ALL_COLORS: tuple[Color, ...] = (COLOR_WHITE, COLOR_BLACK)


class Colors:
    """
    What is true of a colour.
    """

    @staticmethod
    def opponent(color: Color) -> Color:
        return COLOR_BLACK if color == COLOR_WHITE else COLOR_WHITE
