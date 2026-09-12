"""
The draw pile and the discard pile, and moving cards between them.
"""

from idl.uno.model.card_pb2 import Card
from idl.uno.model.game_pb2 import UnoGame, UnoHand

from uno.deck.shuffler import Shuffler

TOP_OF_PILE = 0
SHUFFLE_INCREMENT = 1


class Piles:
    """
    Every move of a card between a pile and a hand.

    Every method edits the game it is handed. The engine calls them on a copy
    it made for the purpose, and hands that copy on once it is whole.
    """

    @staticmethod
    def draw_into_hand(game: UnoGame, hand: UnoHand, count: int) -> tuple[Card, ...]:
        """
        Move up to this many cards from the draw pile into the hand, and
        answer the cards moved. Fewer come when both piles run out.
        """
        drawn: list[Card] = []
        for _ in range(count):
            card = Piles.draw_one(game)
            if card is None:
                break
            hand.cards.append(card)
            drawn.append(card)
        return tuple(drawn)

    @staticmethod
    def draw_one(game: UnoGame) -> Card | None:
        """
        Take the top card of the draw pile, turning the discard pile over
        first when the draw pile is empty. None when there is nothing to draw.
        """
        if len(game.draw_pile) == 0:
            Piles._turn_discards_over(game)
        if len(game.draw_pile) == 0:
            return None
        return game.draw_pile.pop(TOP_OF_PILE)

    @staticmethod
    def discard(game: UnoGame, card: Card) -> None:
        game.discard_pile.append(card)

    @staticmethod
    def get_top_discard(game: UnoGame) -> Card:
        return game.discard_pile[len(game.discard_pile) - 1]

    @staticmethod
    def return_to_bottom(game: UnoGame, cards: tuple[Card, ...]) -> None:
        game.draw_pile.extend(cards)

    @staticmethod
    def _turn_discards_over(game: UnoGame) -> None:
        """
        Shuffle every discard but the top one into a new draw pile.
        """
        buried = tuple(game.discard_pile[: len(game.discard_pile) - 1])
        if len(buried) == 0:
            return
        top = Card()
        top.CopyFrom(Piles.get_top_discard(game))
        game.shuffle_count += SHUFFLE_INCREMENT
        shuffled = Shuffler.shuffle(buried, game.seed, game.shuffle_count)
        del game.discard_pile[:]
        game.discard_pile.append(top)
        del game.draw_pile[:]
        game.draw_pile.extend(shuffled)
