"""
The rules of UNO, as the platform asks them.

The one place that decides what a participant means in UNO: participants act
in the order of their numbers, and a game takes between two and ten of them.
"""

from game.controller.base_rules import BaseRules
from google.protobuf import any_pb2
from idl.game.model.action_pb2 import Action
from idl.game.model.game_spec_pb2 import ParticipantBounds
from idl.game.model.game_state_pb2 import GameState
from idl.game.model.participant_pb2 import ParticipantRole
from uno.engine.uno_engine import MAXIMUM_PARTICIPANTS, MINIMUM_PARTICIPANTS, UnoEngine
from uno.engine.view_projector import ViewProjector

from product_uno.adapters.uno_rules_adapters import UnoRulesAdapters


class UnoRules(BaseRules):
    """
    Every question the platform asks a game, answered for UNO.

    A viewer is shown their own hand and a count of everyone else's. The seed
    fixes the deal and every reshuffle. No state runs out, so no deadline is
    ever expired.
    """

    async def create_game(
        self, participant_roles: tuple[ParticipantRole, ...], seed: int
    ) -> GameState | None:
        participants = UnoRulesAdapters.participant_roles_to_participants(participant_roles)
        game = UnoEngine.new_game(participants, seed)
        if game is None:
            return None
        return UnoRulesAdapters.uno_game_to_game_state(game)

    async def apply_action(self, state: GameState, action: Action) -> GameState | None:
        game = UnoRulesAdapters.game_state_to_uno_game(state)
        if game is None:
            return None
        uno_action = UnoRulesAdapters.action_to_uno_action(action)
        if uno_action is None:
            return None
        advanced = UnoEngine.apply_action(game, action.participant, uno_action)
        if advanced is None:
            return None
        return UnoRulesAdapters.uno_game_to_game_state(advanced)

    async def withdraw_participant(self, state: GameState, participant: int) -> GameState | None:
        """
        A participant who leaves is out of the turn order, and their cards go
        under the draw pile. The last player left wins.
        """
        game = UnoRulesAdapters.game_state_to_uno_game(state)
        if game is None:
            return None
        withdrawn = UnoEngine.withdraw(game, participant)
        if withdrawn is None:
            return None
        return UnoRulesAdapters.uno_game_to_game_state(withdrawn)

    async def read_view(self, state: GameState, participant: int) -> any_pb2.Any:
        game = UnoRulesAdapters.game_state_to_uno_game(state)
        if game is None:
            return any_pb2.Any()
        return UnoRulesAdapters.uno_view_to_payload(ViewProjector.project(game, participant))

    async def expire_deadline(self, state: GameState) -> GameState | None:
        return None

    async def read_bounds(self) -> ParticipantBounds:
        return ParticipantBounds(minimum=MINIMUM_PARTICIPANTS, maximum=MAXIMUM_PARTICIPANTS)
