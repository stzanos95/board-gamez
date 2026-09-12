"""
The kinds of card, and what each one is.
"""

from idl.uno.model.card_pb2 import (
    CARD_KIND_DRAW_TWO,
    CARD_KIND_NUMBER,
    CARD_KIND_REVERSE,
    CARD_KIND_SKIP,
    CARD_KIND_WILD,
    CARD_KIND_WILD_DRAW_FOUR,
    CardKind,
)

WILD_KINDS: tuple[CardKind, ...] = (CARD_KIND_WILD, CARD_KIND_WILD_DRAW_FOUR)
SKIPPING_KINDS: tuple[CardKind, ...] = (
    CARD_KIND_SKIP,
    CARD_KIND_DRAW_TWO,
    CARD_KIND_WILD_DRAW_FOUR,
)

DRAW_TWO_COUNT = 2
DRAW_FOUR_COUNT = 4

CardsDrawnByKind = dict[CardKind, int]

CARDS_DRAWN_BY_KIND: CardsDrawnByKind = {
    CARD_KIND_DRAW_TWO: DRAW_TWO_COUNT,
    CARD_KIND_WILD_DRAW_FOUR: DRAW_FOUR_COUNT,
}


class CardKinds:
    """
    What is true of a kind.
    """

    @staticmethod
    def is_wild(kind: CardKind) -> bool:
        return kind in WILD_KINDS

    @staticmethod
    def is_number(kind: CardKind) -> bool:
        return kind == CARD_KIND_NUMBER

    @staticmethod
    def cards_drawn_by_next(kind: CardKind) -> int:
        """
        How many cards the next player draws when this kind is played; 0 for a
        kind that makes nobody draw.
        """
        return CARDS_DRAWN_BY_KIND.get(kind, 0)

    @staticmethod
    def skips_next(kind: CardKind) -> bool:
        """
        Whether the next player loses their turn when this kind is played.
        Reverse is answered separately, because it skips only with two players.
        """
        return kind in SKIPPING_KINDS

    @staticmethod
    def reverses(kind: CardKind) -> bool:
        return kind == CARD_KIND_REVERSE
