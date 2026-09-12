"""
Every game's rules, asked from outside the process.
"""

from google.protobuf import any_pb2
from idl.game.model.action_pb2 import Action
from idl.game.model.game_spec_pb2 import ParticipantBounds
from idl.game.model.game_state_pb2 import GameState
from idl.game.model.game_type_pb2 import GameType
from idl.game.model.participant_pb2 import ParticipantRole

from game.controller.rules_registry import RulesRegistry


class RulesController:
    """
    RulesService, answered for every hosted game by the rules registered for
    it.

    A game this process does not host answers None to every question. The
    rules themselves decide everything else, so each method is a lookup and a
    call.
    """

    def __init__(self, rules: RulesRegistry) -> None:
        self._rules = rules

    async def create_game(
        self, game_type: GameType, participant_roles: tuple[ParticipantRole, ...], seed: int
    ) -> GameState | None:
        if not self._rules.has_rules(game_type):
            return None
        return await self._rules.get_rules(game_type).create_game(participant_roles, seed)

    async def apply_action(
        self, game_type: GameType, state: GameState, action: Action
    ) -> GameState | None:
        if not self._rules.has_rules(game_type):
            return None
        return await self._rules.get_rules(game_type).apply_action(state, action)

    async def read_view(
        self, game_type: GameType, state: GameState, participant: int
    ) -> any_pb2.Any | None:
        if not self._rules.has_rules(game_type):
            return None
        return await self._rules.get_rules(game_type).read_view(state, participant)

    async def withdraw_participant(
        self, game_type: GameType, state: GameState, participant: int
    ) -> GameState | None:
        if not self._rules.has_rules(game_type):
            return None
        return await self._rules.get_rules(game_type).withdraw_participant(state, participant)

    async def expire_deadline(self, game_type: GameType, state: GameState) -> GameState | None:
        if not self._rules.has_rules(game_type):
            return None
        return await self._rules.get_rules(game_type).expire_deadline(state)

    async def read_bounds(self, game_type: GameType) -> ParticipantBounds | None:
        if not self._rules.has_rules(game_type):
            return None
        return await self._rules.get_rules(game_type).read_bounds()
