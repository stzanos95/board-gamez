"""
What a game's rules are asked, between the arguments a caller has and the
messages the call carries.

A rules client is typed on the domain's models, so the controller holding it
never sees a request. Each conversion here is one direction of one call.
"""

from google.protobuf import any_pb2
from idl.game.dto import rules_pb2
from idl.game.model.action_pb2 import Action
from idl.game.model.game_spec_pb2 import ParticipantBounds
from idl.game.model.game_state_pb2 import GameState


class RulesAdapters:
    """
    Every RulesService message, converted to and from what a caller holds.
    """

    @staticmethod
    def participant_count_to_create_request(
        participant_count: int,
    ) -> rules_pb2.CreateGameRequest:
        return rules_pb2.CreateGameRequest(participant_count=participant_count)

    @staticmethod
    def create_response_to_game_state(response: rules_pb2.CreateGameResponse) -> GameState | None:
        """
        An unset state is how the schema says the game does not take that many.
        """
        return response.state if response.HasField("state") else None

    @staticmethod
    def state_and_action_to_apply_request(
        state: GameState, action: Action
    ) -> rules_pb2.ApplyActionRequest:
        return rules_pb2.ApplyActionRequest(state=state, action=action)

    @staticmethod
    def apply_response_to_game_state(response: rules_pb2.ApplyActionResponse) -> GameState | None:
        """
        An unset state is how the schema says the action was not legal.
        """
        return response.state if response.HasField("state") else None

    @staticmethod
    def state_and_participant_to_view_request(
        state: GameState, participant: int
    ) -> rules_pb2.ReadViewRequest:
        return rules_pb2.ReadViewRequest(state=state, participant=participant)

    @staticmethod
    def view_response_to_view(response: rules_pb2.ReadViewResponse) -> any_pb2.Any:
        return response.view

    @staticmethod
    def bounds_request() -> rules_pb2.ReadBoundsRequest:
        return rules_pb2.ReadBoundsRequest()

    @staticmethod
    def bounds_response_to_bounds(response: rules_pb2.ReadBoundsResponse) -> ParticipantBounds:
        return response.bounds
