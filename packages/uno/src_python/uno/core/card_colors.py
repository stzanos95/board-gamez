"""
The four colours a card can follow.
"""

from idl.uno.model.card_pb2 import (
    CARD_COLOR_BLUE,
    CARD_COLOR_GREEN,
    CARD_COLOR_RED,
    CARD_COLOR_UNSPECIFIED,
    CARD_COLOR_YELLOW,
    CardColor,
)

ALL_CARD_COLORS: tuple[CardColor, ...] = (
    CARD_COLOR_RED,
    CARD_COLOR_YELLOW,
    CARD_COLOR_GREEN,
    CARD_COLOR_BLUE,
)


class CardColors:
    """
    What is true of a colour.
    """

    @staticmethod
    def is_named(color: CardColor) -> bool:
        """
        Whether the colour is one of the four a card can follow.
        """
        return color != CARD_COLOR_UNSPECIFIED and color in ALL_CARD_COLORS
