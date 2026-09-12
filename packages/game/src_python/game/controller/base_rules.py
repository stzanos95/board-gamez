"""
What a game's rules answer, as the session layer asks them.
"""

from abc import ABC, abstractmethod

from google.protobuf import any_pb2
from idl.game.model.action_pb2 import Action
from idl.game.model.game_spec_pb2 import ParticipantBounds
from idl.game.model.game_state_pb2 import GameState
from idl.game.model.participant_pb2 import ParticipantRole


class BaseRules(ABC):
    """
    One game's rules, whichever game.

    Typed on the domain's models, so a controller holding one never sees a
    request. Every call carries the state it acts on; nothing is held between
    calls on either side.
    """

    @abstractmethod
    async def create_game(
        self, participant_roles: tuple[ParticipantRole, ...], seed: int
    ) -> GameState | None:
        """
        The opening state of a game for these participants, numbered 1 through
        N and each carrying the role it was seated with, or None when the game
        does not take them.

        `seed` is what every draw of chance in the game is taken from. A game
        with no chance in it does not read it.
        """

    @abstractmethod
    async def apply_action(self, state: GameState, action: Action) -> GameState | None:
        """
        The state after this action, or None when the action is not legal in
        this state.
        """

    @abstractmethod
    async def read_view(self, state: GameState, participant: int) -> any_pb2.Any:
        """
        The game as this participant may see it. Participant 0 is someone who
        is not playing.
        """

    @abstractmethod
    async def withdraw_participant(self, state: GameState, participant: int) -> GameState | None:
        """
        The state after this participant leaves the game, or None when the
        participant is not in it. Asked in or out of turn, and never once the
        game has a result.
        """

    @abstractmethod
    async def expire_deadline(self, state: GameState) -> GameState | None:
        """
        The state after this one stood until its deadline with nobody acting,
        or None when the state carries no deadline. Never asked once the game
        has a result.
        """

    @abstractmethod
    async def read_bounds(self) -> ParticipantBounds:
        """
        How many participants the game takes.
        """
