"""
Games set up by hand, so a test names the cards it needs.
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
)
from idl.uno.model.game_pb2 import PLAY_DIRECTION_CLOCKWISE, UnoGame

SEED = 12345
FIRST_SHUFFLE = 1


def number(color: CardColor, value: int) -> Card:
    return Card(kind=CARD_KIND_NUMBER, color=color, number=value)


def skip(color: CardColor) -> Card:
    return Card(kind=CARD_KIND_SKIP, color=color)


def reverse(color: CardColor) -> Card:
    return Card(kind=CARD_KIND_REVERSE, color=color)


def draw_two(color: CardColor) -> Card:
    return Card(kind=CARD_KIND_DRAW_TWO, color=color)


def wild() -> Card:
    return Card(kind=CARD_KIND_WILD)


def wild_draw_four() -> Card:
    return Card(kind=CARD_KIND_WILD_DRAW_FOUR)


class GameBuilder:
    """
    A game whose hands, piles and turn a test chose.
    """

    @staticmethod
    def build(
        hands: dict[int, tuple[Card, ...]],
        draw_pile: tuple[Card, ...],
        top: Card,
        active_color: CardColor,
        participant_to_act: int,
    ) -> UnoGame:
        game = UnoGame(
            active_color=active_color,
            direction=PLAY_DIRECTION_CLOCKWISE,
            participant_to_act=participant_to_act,
            seed=SEED,
            shuffle_count=FIRST_SHUFFLE,
        )
        for participant, cards in hands.items():
            hand = game.hands.add()
            hand.participant = participant
            hand.cards.extend(cards)
        game.draw_pile.extend(draw_pile)
        game.discard_pile.append(top)
        return game
