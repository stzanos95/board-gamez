"""
Whose turn comes after whose.
"""

from idl.uno.model.game_pb2 import UnoGame, UnoHand

from uno.core.play_directions import PlayDirections

NO_PARTICIPANT = 0
ONE_STEP = 1
TWO_STEPS = 2


class TurnOrder:
    """
    The order play passes around the table.

    Hands sit in participant order, and play moves along them in the game's
    direction, wrapping at either end. A hand that has withdrawn is passed
    over without counting as a step.
    """

    @staticmethod
    def get_hand(game: UnoGame, participant: int) -> UnoHand | None:
        for hand in game.hands:
            if hand.participant == participant:
                return hand
        return None

    @staticmethod
    def get_active_participants(game: UnoGame) -> tuple[int, ...]:
        return tuple(hand.participant for hand in game.hands if not hand.has_withdrawn)

    @staticmethod
    def get_participant_after(game: UnoGame, participant: int, steps: int) -> int:
        """
        The participant this many turns after the one named, in the game's
        direction; NO_PARTICIPANT when nobody is left to act.
        """
        active = TurnOrder.get_active_participants(game)
        if len(active) == 0:
            return NO_PARTICIPANT
        index = TurnOrder._get_index(game, participant)
        step = PlayDirections.step(game.direction)
        count = len(game.hands)
        remaining = steps
        while remaining > 0:
            index = (index + step) % count
            if not game.hands[index].has_withdrawn:
                remaining -= 1
        return game.hands[index].participant

    @staticmethod
    def _get_index(game: UnoGame, participant: int) -> int:
        for index, hand in enumerate(game.hands):
            if hand.participant == participant:
                return index
        raise ValueError(f"participant {participant} holds no hand in this game")
