"""
The game as one participant may see it.
"""

from idl.uno.model.game_pb2 import UnoGame
from idl.uno.model.view_pb2 import UnoView

from uno.engine.piles import Piles
from uno.engine.turn_order import TurnOrder
from uno.engine.uno_engine import UnoEngine


class ViewProjector:
    """
    What is shown to whom.

    Every viewer sees the top of the discard pile, the active colour, whose
    turn it is, and how many cards everyone holds. A participant sees their
    own cards and which of them may be played now. Nobody sees the draw pile
    or another hand.
    """

    @staticmethod
    def project(game: UnoGame, participant: int) -> UnoView:
        view = UnoView(
            active_color=game.active_color,
            direction=game.direction,
            participant_to_act=game.participant_to_act,
            draw_pile_count=len(game.draw_pile),
            may_draw=UnoEngine.may_draw(game, participant),
            may_pass=UnoEngine.may_pass(game, participant),
        )
        for hand in game.hands:
            summary = view.players.add()
            summary.participant = hand.participant
            summary.card_count = len(hand.cards)
            summary.has_withdrawn = hand.has_withdrawn
        if len(game.discard_pile) > 0:
            view.top_card.CopyFrom(Piles.get_top_discard(game))
        if game.HasField("result"):
            view.result.CopyFrom(game.result)
        own = TurnOrder.get_hand(game, participant)
        if own is not None:
            for card in own.cards:
                shown = view.hand.add()
                shown.card.CopyFrom(card)
                shown.is_playable = UnoEngine.is_playable(game, participant, card)
            if game.HasField("drawn_card") and game.participant_to_act == participant:
                view.drawn_card.CopyFrom(game.drawn_card)
        return view
