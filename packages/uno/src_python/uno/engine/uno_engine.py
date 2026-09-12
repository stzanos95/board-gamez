"""
The game: a new deal, what an action does, and how a game ends.
"""

from idl.uno.model.action_pb2 import CardPlay, UnoAction
from idl.uno.model.card_pb2 import CARD_KIND_NUMBER, Card
from idl.uno.model.game_pb2 import (
    PLAY_DIRECTION_CLOCKWISE,
    UNO_RESULT_REASON_HAND_EMPTIED,
    UNO_RESULT_REASON_OTHERS_WITHDREW,
    UnoGame,
    UnoHand,
    UnoResult,
    UnoResultReason,
)

from uno.core.card_colors import CardColors
from uno.core.card_kinds import CardKinds
from uno.core.cards import Cards
from uno.core.play_directions import PlayDirections
from uno.deck.deck_builder import DeckBuilder
from uno.deck.shuffler import Shuffler
from uno.engine.piles import Piles
from uno.engine.play_legality import PlayLegality
from uno.engine.turn_order import NO_PARTICIPANT, ONE_STEP, TWO_STEPS, TurnOrder

HAND_SIZE = 7
FIRST_SHUFFLE = 1
MINIMUM_PARTICIPANTS = 2
MAXIMUM_PARTICIPANTS = 10
# With two players a Reverse passes the turn straight back, so it acts as a Skip.
REVERSE_SKIPS_AT = 2
LAST_PLAYER_STANDING = 1


class UnoEngine:
    """
    Every question the rules answer, over the schema's own record of a game.

    A game handed in is never edited. Each method that answers a new game
    copies the one it was given and edits the copy.
    """

    @staticmethod
    def new_game(participants: tuple[int, ...], seed: int) -> UnoGame | None:
        """
        A fresh deal for these participants, who act in the order given, or
        None when the game does not take that many.

        The first card turned over is a number card. An action card or a wild
        drawn there goes under the draw pile, and the next card is tried.
        """
        if not MINIMUM_PARTICIPANTS <= len(participants) <= MAXIMUM_PARTICIPANTS:
            return None
        game = UnoGame(
            direction=PLAY_DIRECTION_CLOCKWISE,
            participant_to_act=participants[0],
            seed=seed,
            shuffle_count=FIRST_SHUFFLE,
        )
        game.draw_pile.extend(Shuffler.shuffle(DeckBuilder.build_deck(), seed, FIRST_SHUFFLE))
        for participant in participants:
            hand = game.hands.add()
            hand.participant = participant
            Piles.draw_into_hand(game, hand, HAND_SIZE)
        first = Piles.draw_one(game)
        while first is not None and first.kind != CARD_KIND_NUMBER:
            Piles.return_to_bottom(game, (first,))
            first = Piles.draw_one(game)
        if first is None:
            return None
        Piles.discard(game, first)
        game.active_color = first.color
        return game

    @staticmethod
    def apply_action(game: UnoGame, participant: int, action: UnoAction) -> UnoGame | None:
        """
        The game after this participant does this, or None when the action is
        not theirs to take or not legal now.
        """
        if game.HasField("result") or participant != game.participant_to_act:
            return None
        hand = TurnOrder.get_hand(game, participant)
        if hand is None or hand.has_withdrawn:
            return None
        if action.HasField("play"):
            return UnoEngine._play(game, participant, action.play)
        if action.HasField("draw"):
            return UnoEngine._draw(game, participant)
        if action.HasField("pass"):
            return UnoEngine._pass(game, participant)
        return None

    @staticmethod
    def withdraw(game: UnoGame, participant: int) -> UnoGame | None:
        """
        The game with this participant out of it, or None when they are not
        in it. Their cards go under the draw pile. When one player is left,
        that player wins.
        """
        hand = TurnOrder.get_hand(game, participant)
        if hand is None or hand.has_withdrawn:
            return None
        next_game = UnoEngine._copy(game)
        next_hand = UnoEngine._require_hand(next_game, participant)
        Piles.return_to_bottom(next_game, tuple(next_hand.cards))
        del next_hand.cards[:]
        next_hand.has_withdrawn = True
        if next_game.HasField("drawn_card") and next_game.participant_to_act == participant:
            next_game.ClearField("drawn_card")
        active = TurnOrder.get_active_participants(next_game)
        if len(active) <= LAST_PLAYER_STANDING:
            winner = active[0] if len(active) == LAST_PLAYER_STANDING else NO_PARTICIPANT
            UnoEngine._finish(next_game, winner, UNO_RESULT_REASON_OTHERS_WITHDREW)
        elif next_game.participant_to_act == participant:
            next_game.participant_to_act = TurnOrder.get_participant_after(
                next_game, participant, ONE_STEP
            )
        return next_game

    @staticmethod
    def is_playable(game: UnoGame, participant: int, card: Card) -> bool:
        """
        Whether this participant may play this card now.
        """
        if game.HasField("result") or participant != game.participant_to_act:
            return False
        hand = TurnOrder.get_hand(game, participant)
        if hand is None or hand.has_withdrawn:
            return False
        return PlayLegality.is_playable(game, hand, card)

    @staticmethod
    def may_draw(game: UnoGame, participant: int) -> bool:
        return (
            not game.HasField("result")
            and participant == game.participant_to_act
            and not game.HasField("drawn_card")
        )

    @staticmethod
    def may_pass(game: UnoGame, participant: int) -> bool:
        return (
            not game.HasField("result")
            and participant == game.participant_to_act
            and game.HasField("drawn_card")
        )

    # --- one action each -----------------------------------------------------

    @staticmethod
    def _play(game: UnoGame, participant: int, play: CardPlay) -> UnoGame | None:
        hand = UnoEngine._require_hand(game, participant)
        card = play.card
        if not PlayLegality.is_playable(game, hand, card):
            return None
        if Cards.is_wild(card) != CardColors.is_named(play.chosen_color):
            return None
        next_game = UnoEngine._copy(game)
        next_hand = UnoEngine._require_hand(next_game, participant)
        UnoEngine._remove_from_hand(next_hand, card)
        Piles.discard(next_game, card)
        next_game.ClearField("drawn_card")
        next_game.active_color = play.chosen_color if Cards.is_wild(card) else card.color
        UnoEngine._apply_card_effect(next_game, participant, card)
        if len(next_hand.cards) == 0:
            UnoEngine._finish(next_game, participant, UNO_RESULT_REASON_HAND_EMPTIED)
        return next_game

    @staticmethod
    def _draw(game: UnoGame, participant: int) -> UnoGame | None:
        if game.HasField("drawn_card"):
            return None
        next_game = UnoEngine._copy(game)
        next_hand = UnoEngine._require_hand(next_game, participant)
        drawn = Piles.draw_into_hand(next_game, next_hand, ONE_STEP)
        if len(drawn) == 0:
            # Nothing left to draw anywhere: the turn passes.
            next_game.participant_to_act = TurnOrder.get_participant_after(
                next_game, participant, ONE_STEP
            )
            return next_game
        next_game.drawn_card.CopyFrom(drawn[0])
        return next_game

    @staticmethod
    def _pass(game: UnoGame, participant: int) -> UnoGame | None:
        if not game.HasField("drawn_card"):
            return None
        next_game = UnoEngine._copy(game)
        next_game.ClearField("drawn_card")
        next_game.participant_to_act = TurnOrder.get_participant_after(
            next_game, participant, ONE_STEP
        )
        return next_game

    # --- what a card does ----------------------------------------------------

    @staticmethod
    def _apply_card_effect(game: UnoGame, participant: int, card: Card) -> None:
        """
        Turn the direction, make the next player draw, and move the turn on
        by one or two, as the card says.
        """
        if CardKinds.reverses(card.kind):
            game.direction = PlayDirections.reversed(game.direction)
        drawn_by_next = CardKinds.cards_drawn_by_next(card.kind)
        if drawn_by_next > 0:
            following = TurnOrder.get_participant_after(game, participant, ONE_STEP)
            Piles.draw_into_hand(game, UnoEngine._require_hand(game, following), drawn_by_next)
        active_count = len(TurnOrder.get_active_participants(game))
        reverse_skips = CardKinds.reverses(card.kind) and active_count == REVERSE_SKIPS_AT
        steps = TWO_STEPS if CardKinds.skips_next(card.kind) or reverse_skips else ONE_STEP
        game.participant_to_act = TurnOrder.get_participant_after(game, participant, steps)

    @staticmethod
    def _finish(game: UnoGame, winner: int, reason: UnoResultReason) -> None:
        game.result.CopyFrom(UnoResult(winner=winner, reason=reason))
        game.participant_to_act = NO_PARTICIPANT
        game.ClearField("drawn_card")

    # --- plumbing ------------------------------------------------------------

    @staticmethod
    def _copy(game: UnoGame) -> UnoGame:
        copied = UnoGame()
        copied.CopyFrom(game)
        return copied

    @staticmethod
    def _require_hand(game: UnoGame, participant: int) -> UnoHand:
        hand = TurnOrder.get_hand(game, participant)
        if hand is None:
            raise ValueError(f"participant {participant} holds no hand in this game")
        return hand

    @staticmethod
    def _remove_from_hand(hand: UnoHand, card: Card) -> None:
        for index, held in enumerate(hand.cards):
            if held == card:
                del hand.cards[index]
                return
        raise ValueError(f"the hand does not hold {card}")
