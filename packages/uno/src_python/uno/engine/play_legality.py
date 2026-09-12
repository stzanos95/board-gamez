"""
Whether a card may be played from a hand right now.
"""

from idl.uno.model.card_pb2 import CARD_KIND_WILD_DRAW_FOUR, Card
from idl.uno.model.game_pb2 import UnoGame, UnoHand

from uno.core.cards import Cards
from uno.engine.piles import Piles


class PlayLegality:
    """
    The rules that decide a play, given that it is the hand's turn.
    """

    @staticmethod
    def is_playable(game: UnoGame, hand: UnoHand, card: Card) -> bool:
        """
        Whether this card may be played from this hand onto the game as it
        stands.

        A card must be in the hand and follow the top card. After a draw, only
        the card drawn may be played. A Wild Draw Four may be played only by a
        hand holding no card of the active colour.
        """
        if not PlayLegality._holds(hand, card):
            return False
        if game.HasField("drawn_card") and card != game.drawn_card:
            return False
        if not Cards.follows(card, Piles.get_top_discard(game), game.active_color):
            return False
        if card.kind == CARD_KIND_WILD_DRAW_FOUR:
            return not any(Cards.has_color(held, game.active_color) for held in hand.cards)
        return True

    @staticmethod
    def _holds(hand: UnoHand, card: Card) -> bool:
        return any(held == card for held in hand.cards)
