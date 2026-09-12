"""
What one card may do against another.
"""

from idl.uno.model.card_pb2 import Card, CardColor

from uno.core.card_kinds import CardKinds


class Cards:
    """
    What is true of a card.
    """

    @staticmethod
    def is_wild(card: Card) -> bool:
        return CardKinds.is_wild(card.kind)

    @staticmethod
    def follows(card: Card, top: Card, active_color: CardColor) -> bool:
        """
        Whether this card may be played onto the top card while the active
        colour is what it is.

        A wild follows anything. A coloured card follows the active colour, a
        number card of the same number, or an action card of the same kind.
        """
        if Cards.is_wild(card):
            return True
        if card.color == active_color:
            return True
        if CardKinds.is_number(card.kind):
            return CardKinds.is_number(top.kind) and card.number == top.number
        return card.kind == top.kind

    @staticmethod
    def has_color(card: Card, color: CardColor) -> bool:
        """
        Whether the card is a coloured card of this colour. A wild has no colour.
        """
        return not Cards.is_wild(card) and card.color == color
