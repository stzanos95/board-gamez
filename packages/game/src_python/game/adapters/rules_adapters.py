"""
RulesService, between a request and the arguments the rules take.

Every conversion between a RulesService message and the platform's own types
runs here, one named method per direction, so the servicer reads no field off
a request.
"""

from google.protobuf import any_pb2
from idl.game.dto import rules_pb2
from idl.game.model.action_pb2 import Action
from idl.game.model.game_spec_pb2 import ParticipantBounds
from idl.game.model.game_state_pb2 import GameState
from idl.game.model.game_type_pb2 import GameType
from idl.game.model.participant_pb2 import ParticipantRole


class RulesAdapters:
    """
    Every RulesService message, converted to what the controller takes and
    back.
    """

    # --- a request, to the arguments an operation takes ----------------------

    @staticmethod
    def create_request_to_game_type(request: rules_pb2.CreateGameRequest) -> GameType:
        return request.game_type

    @staticmethod
    def create_request_to_participant_roles(
        request: rules_pb2.CreateGameRequest,
    ) -> tuple[ParticipantRole, ...]:
        return tuple(request.participant_roles)

    @staticmethod
    def create_request_to_seed(request: rules_pb2.CreateGameRequest) -> int:
        return request.seed

    @staticmethod
    def apply_request_to_game_type(request: rules_pb2.ApplyActionRequest) -> GameType:
        return request.game_type

    @staticmethod
    def apply_request_to_state(request: rules_pb2.ApplyActionRequest) -> GameState:
        return request.state

    @staticmethod
    def apply_request_to_action(request: rules_pb2.ApplyActionRequest) -> Action:
        return request.action

    @staticmethod
    def view_request_to_game_type(request: rules_pb2.ReadViewRequest) -> GameType:
        return request.game_type

    @staticmethod
    def view_request_to_state(request: rules_pb2.ReadViewRequest) -> GameState:
        return request.state

    @staticmethod
    def view_request_to_participant(request: rules_pb2.ReadViewRequest) -> int:
        return request.participant

    @staticmethod
    def withdraw_request_to_game_type(
        request: rules_pb2.WithdrawParticipantRequest,
    ) -> GameType:
        return request.game_type

    @staticmethod
    def withdraw_request_to_state(request: rules_pb2.WithdrawParticipantRequest) -> GameState:
        return request.state

    @staticmethod
    def withdraw_request_to_participant(request: rules_pb2.WithdrawParticipantRequest) -> int:
        return request.participant

    @staticmethod
    def expire_request_to_game_type(request: rules_pb2.ExpireDeadlineRequest) -> GameType:
        return request.game_type

    @staticmethod
    def expire_request_to_state(request: rules_pb2.ExpireDeadlineRequest) -> GameState:
        return request.state

    @staticmethod
    def bounds_request_to_game_type(request: rules_pb2.ReadBoundsRequest) -> GameType:
        return request.game_type

    # --- what an operation answers, to a response ----------------------------

    @staticmethod
    def game_state_to_create_response(state: GameState | None) -> rules_pb2.CreateGameResponse:
        """
        An unset state is how the schema says the game is not hosted or does
        not take these participants.
        """
        return rules_pb2.CreateGameResponse(state=state)

    @staticmethod
    def game_state_to_apply_response(state: GameState | None) -> rules_pb2.ApplyActionResponse:
        """
        An unset state is how the schema says the game is not hosted or the
        action was not legal.
        """
        return rules_pb2.ApplyActionResponse(state=state)

    @staticmethod
    def view_to_view_response(view: any_pb2.Any | None) -> rules_pb2.ReadViewResponse:
        """
        An unset view is how the schema says the game is not hosted.
        """
        return rules_pb2.ReadViewResponse(view=view)

    @staticmethod
    def game_state_to_withdraw_response(
        state: GameState | None,
    ) -> rules_pb2.WithdrawParticipantResponse:
        """
        An unset state is how the schema says the game is not hosted or the
        participant is not in it.
        """
        return rules_pb2.WithdrawParticipantResponse(state=state)

    @staticmethod
    def game_state_to_expire_response(
        state: GameState | None,
    ) -> rules_pb2.ExpireDeadlineResponse:
        """
        An unset state is how the schema says the game is not hosted or the
        state carried no deadline.
        """
        return rules_pb2.ExpireDeadlineResponse(state=state)

    @staticmethod
    def bounds_to_bounds_response(
        bounds: ParticipantBounds | None,
    ) -> rules_pb2.ReadBoundsResponse:
        """
        Unset bounds are how the schema says the game is not hosted.
        """
        return rules_pb2.ReadBoundsResponse(bounds=bounds)
