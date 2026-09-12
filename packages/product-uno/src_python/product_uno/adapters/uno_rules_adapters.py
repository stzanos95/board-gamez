"""
UNO, between the platform's types and the game's own.

The platform carries a game's state and a participant's action opaquely. Every
conversion between what the platform holds and what the engine takes runs
here, one named method per direction.
"""

from google.protobuf import any_pb2
from idl.game.model.action_pb2 import Action
from idl.game.model.game_result_pb2 import GameResult, ParticipantOutcome, ParticipantResult
from idl.game.model.game_state_pb2 import GameState
from idl.game.model.participant_pb2 import ParticipantRole
from idl.game.model.participant_state_pb2 import (
    ParticipantState,
    ParticipantStateKind,
    ParticipantStatus,
)
from idl.uno.model.action_pb2 import UnoAction
from idl.uno.model.game_pb2 import UnoGame, UnoHand, UnoResult
from idl.uno.model.view_pb2 import UnoView

NOBODY_TO_ACT: tuple[int, ...] = ()
NO_WINNER = 0
LAST_CARD = 1


class UnoRulesAdapters:
    """
    Every platform type, converted to what UNO takes and back.
    """

    # --- the platform's state and action, to UNO's ---------------------------

    @staticmethod
    def game_state_to_uno_game(state: GameState) -> UnoGame | None:
        """
        The UNO game the state carries, or None when the payload is not one.
        """
        game = UnoGame()
        if not state.payload.Unpack(game):
            return None
        return game

    @staticmethod
    def action_to_uno_action(action: Action) -> UnoAction | None:
        """
        The UNO action the action carries, or None when the payload is not one.
        """
        uno_action = UnoAction()
        if not action.payload.Unpack(uno_action):
            return None
        return uno_action

    # --- the platform's roles, to UNO's turn order ---------------------------

    @staticmethod
    def participant_roles_to_participants(
        participant_roles: tuple[ParticipantRole, ...],
    ) -> tuple[int, ...]:
        """
        The participants in the order they act: by number, lowest first. A
        role is not read; UNO seats carry none.
        """
        return tuple(sorted(role.participant for role in participant_roles))

    # --- the game, to the platform's state ----------------------------------

    @staticmethod
    def uno_game_to_game_state(game: UnoGame) -> GameState:
        """
        The game as the platform holds it: the whole game packed, who acts
        next, what everyone may see of each participant, and the result once
        there is one. UNO has no clock here, so no state runs out.
        """
        is_over = game.HasField("result")
        return GameState(
            payload=UnoRulesAdapters.uno_game_to_payload(game),
            participants_to_act=NOBODY_TO_ACT if is_over else (game.participant_to_act,),
            result=UnoRulesAdapters.uno_result_to_game_result(game) if is_over else None,
            participant_statuses=[
                UnoRulesAdapters.uno_hand_to_participant_status(hand) for hand in game.hands
            ],
        )

    @staticmethod
    def uno_hand_to_participant_status(hand: UnoHand) -> ParticipantStatus:
        """
        What everyone may see of one hand: how many cards it holds, that it is
        down to its last card, or that its player has left.
        """
        if hand.has_withdrawn:
            return ParticipantStatus(
                participant=hand.participant,
                states=[
                    ParticipantState(kind=ParticipantStateKind.PARTICIPANT_STATE_KIND_WITHDRAWN)
                ],
            )
        states = [
            ParticipantState(
                kind=ParticipantStateKind.PARTICIPANT_STATE_KIND_HOLDING, count=len(hand.cards)
            )
        ]
        if len(hand.cards) == LAST_CARD:
            states.append(
                ParticipantState(kind=ParticipantStateKind.PARTICIPANT_STATE_KIND_LAST_ONE)
            )
        return ParticipantStatus(participant=hand.participant, states=states)

    @staticmethod
    def uno_game_to_payload(game: UnoGame) -> any_pb2.Any:
        payload = any_pb2.Any()
        payload.Pack(game)
        return payload

    @staticmethod
    def uno_view_to_payload(view: UnoView) -> any_pb2.Any:
        payload = any_pb2.Any()
        payload.Pack(view)
        return payload

    @staticmethod
    def uno_result_to_game_result(game: UnoGame) -> GameResult:
        """
        One entry per participant. The winner won and everyone else lost,
        whether they were still playing or had withdrawn. A game with no winner
        scores everyone as drawn.
        """
        result: UnoResult = game.result
        return GameResult(
            participant_items=[
                ParticipantResult(
                    participant=hand.participant,
                    outcome=UnoRulesAdapters._outcome_of(hand.participant, result.winner),
                )
                for hand in game.hands
            ]
        )

    @staticmethod
    def _outcome_of(participant: int, winner: int) -> ParticipantOutcome:
        if winner == NO_WINNER:
            return ParticipantOutcome.PARTICIPANT_OUTCOME_DRAW
        if participant == winner:
            return ParticipantOutcome.PARTICIPANT_OUTCOME_WON
        return ParticipantOutcome.PARTICIPANT_OUTCOME_LOST
