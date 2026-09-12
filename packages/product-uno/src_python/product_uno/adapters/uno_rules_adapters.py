"""
UNO, between the platform's types and the game's own.

The platform carries a game's state and a participant's action opaquely, and
asks the rules through RulesService. Every conversion between what the platform
holds and what the engine takes runs here, one named method per direction.
"""

from google.protobuf import any_pb2
from idl.game.dto import rules_pb2
from idl.game.model.action_pb2 import Action
from idl.game.model.game_result_pb2 import GameResult, ParticipantOutcome, ParticipantResult
from idl.game.model.game_spec_pb2 import ParticipantBounds
from idl.game.model.game_state_pb2 import GameState
from idl.game.model.participant_pb2 import ParticipantRole
from idl.uno.model.action_pb2 import UnoAction
from idl.uno.model.game_pb2 import UnoGame, UnoResult
from idl.uno.model.view_pb2 import UnoView

NOBODY_TO_ACT: tuple[int, ...] = ()
NO_WINNER = 0


class UnoRulesAdapters:
    """
    Every RulesService message and every platform type, converted to what UNO
    takes and back.
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

    @staticmethod
    def withdraw_request_to_state(request: rules_pb2.WithdrawParticipantRequest) -> GameState:
        return request.state

    @staticmethod
    def withdraw_request_to_participant(request: rules_pb2.WithdrawParticipantRequest) -> int:
        return request.participant

    @staticmethod
    def game_state_to_withdraw_response(
        state: GameState | None,
    ) -> rules_pb2.WithdrawParticipantResponse:
        """
        An unset state is how the schema says the participant is not in the
        game.
        """
        return rules_pb2.WithdrawParticipantResponse(state=state)

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
        next, and the result once there is one. UNO has no clock here, so no
        state runs out.
        """
        is_over = game.HasField("result")
        return GameState(
            payload=UnoRulesAdapters.uno_game_to_payload(game),
            participants_to_act=NOBODY_TO_ACT if is_over else (game.participant_to_act,),
            result=UnoRulesAdapters.uno_result_to_game_result(game) if is_over else None,
        )

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

    # --- a request, to the arguments an operation takes ----------------------

    @staticmethod
    def create_request_to_participant_roles(
        request: rules_pb2.CreateGameRequest,
    ) -> tuple[ParticipantRole, ...]:
        return tuple(request.participant_roles)

    @staticmethod
    def create_request_to_seed(request: rules_pb2.CreateGameRequest) -> int:
        return request.seed

    @staticmethod
    def apply_request_to_state(request: rules_pb2.ApplyActionRequest) -> GameState:
        return request.state

    @staticmethod
    def expire_request_to_state(request: rules_pb2.ExpireDeadlineRequest) -> GameState:
        return request.state

    @staticmethod
    def apply_request_to_action(request: rules_pb2.ApplyActionRequest) -> Action:
        return request.action

    @staticmethod
    def view_request_to_state(request: rules_pb2.ReadViewRequest) -> GameState:
        return request.state

    @staticmethod
    def view_request_to_participant(request: rules_pb2.ReadViewRequest) -> int:
        return request.participant

    # --- what an operation answers, to a response ----------------------------

    @staticmethod
    def game_state_to_create_response(state: GameState | None) -> rules_pb2.CreateGameResponse:
        """
        An unset state is how the schema says the game does not take that many.
        """
        return rules_pb2.CreateGameResponse(state=state)

    @staticmethod
    def game_state_to_apply_response(state: GameState | None) -> rules_pb2.ApplyActionResponse:
        """
        An unset state is how the schema says the action was not legal.
        """
        return rules_pb2.ApplyActionResponse(state=state)

    @staticmethod
    def game_state_to_expire_response(
        state: GameState | None,
    ) -> rules_pb2.ExpireDeadlineResponse:
        """
        An unset state is how the schema says the state carried no deadline.
        """
        return rules_pb2.ExpireDeadlineResponse(state=state)

    @staticmethod
    def view_to_view_response(view: any_pb2.Any) -> rules_pb2.ReadViewResponse:
        return rules_pb2.ReadViewResponse(view=view)

    @staticmethod
    def bounds_to_bounds_response(bounds: ParticipantBounds) -> rules_pb2.ReadBoundsResponse:
        return rules_pb2.ReadBoundsResponse(bounds=bounds)
