"""
The 108 cards a game is played with.
"""

from idl.uno.model.card_pb2 import (
    CARD_KIND_DRAW_TWO,
    CARD_KIND_NUMBER,
    CARD_KIND_REVERSE,
    CARD_KIND_SKIP,
    CARD_KIND_WILD,
    CARD_KIND_WILD_DRAW_FOUR,
    Card,
    CardColor,
    CardKind,
)

from uno.core.card_colors import ALL_CARD_COLORS

LOWEST_NUMBER = 0
HIGHEST_NUMBER = 9
# One 0 per colour, and two of every other number.
SINGLE_NUMBER = 0
SINGLE_COPY = 1
COLORED_ACTION_COPIES = 2
WILD_COPIES = 4
DECK_SIZE = 108

COLORED_ACTION_KINDS_DEALT: tuple[CardKind, ...] = (
    CARD_KIND_SKIP,
    CARD_KIND_REVERSE,
    CARD_KIND_DRAW_TWO,
)
WILD_KINDS_DEALT: tuple[CardKind, ...] = (CARD_KIND_WILD, CARD_KIND_WILD_DRAW_FOUR)


class DeckBuilder:
    """
    The full deck, in a fixed order a shuffle then rearranges.
    """

    @staticmethod
    def build_deck() -> tuple[Card, ...]:
        cards: list[Card] = []
        for color in ALL_CARD_COLORS:
            cards.extend(DeckBuilder._build_color(color))
        for kind in WILD_KINDS_DEALT:
            cards.extend(Card(kind=kind) for _ in range(WILD_COPIES))
        return tuple(cards)

    @staticmethod
    def _build_color(color: CardColor) -> tuple[Card, ...]:
        cards: list[Card] = []
        for number in range(LOWEST_NUMBER, HIGHEST_NUMBER + 1):
            copies = SINGLE_COPY if number == SINGLE_NUMBER else COLORED_ACTION_COPIES
            cards.extend(
                Card(kind=CARD_KIND_NUMBER, color=color, number=number) for _ in range(copies)
            )
        for kind in COLORED_ACTION_KINDS_DEALT:
            cards.extend(Card(kind=kind, color=color) for _ in range(COLORED_ACTION_COPIES))
        return tuple(cards)
