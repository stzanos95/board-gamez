"""
A game whose rules are simple enough to script.

The position is a count of the actions applied. An action is a word: MOVE is
always legal and passes the turn to the next participant, WIN ends the game with
the acting participant winning, and anything else is illegal. The view a
participant gets names both the position and the participant, so a test can see
that projection happened for the right one.

Given `acts_within`, every state still being played carries it, and a state
that runs out passes the turn as a MOVE by the first participant to act would.
The seed handed at creation is kept, so a test can see it arrived.
"""

from dataclasses import dataclass

from google.protobuf import any_pb2
from google.protobuf.duration_pb2 import Duration
from google.protobuf.wrappers_pb2 import StringValue, UInt32Value
from idl.game.model.action_pb2 import Action
from idl.game.model.game_result_pb2 import GameResult, ParticipantOutcome, ParticipantResult
from idl.game.model.game_spec_pb2 import ParticipantBounds
from idl.game.model.game_state_pb2 import GameState
from idl.game.model.participant_pb2 import ParticipantRole

from game.controller.base_rules import BaseRules

MOVE = "move"
WIN = "win"
OPENING_POSITION = 0
FIRST_PARTICIPANT = 1
NOBODY = 0
VIEW_SEPARATOR = ":"
PARTICIPANT_COUNT_RADIX = 100


@dataclass(frozen=True, slots=True)
class ScriptedPosition:
    """
    Where a scripted game stands: how many actions were applied, and how many
    are playing.
    """

    position: int
    participant_count: int


class ScriptedRules(BaseRules):
    """
    Rules that a test can predict, for a game of a configurable size.
    """

    def __init__(self, minimum: int, maximum: int, acts_within: Duration | None = None) -> None:
        self._bounds = ParticipantBounds(minimum=minimum, maximum=maximum)
        self._acts_within = acts_within
        self.seeds_received: list[int] = []

    async def create_game(
        self, participant_roles: tuple[ParticipantRole, ...], seed: int
    ) -> GameState | None:
        self.seeds_received.append(seed)
        participant_count = len(participant_roles)
        if not self._bounds.minimum <= participant_count <= self._bounds.maximum:
            return None
        return GameState(
            payload=ScriptedRules.position_payload(OPENING_POSITION, participant_count),
            participants_to_act=[FIRST_PARTICIPANT],
            acts_within=self._acts_within,
        )

    async def apply_action(self, state: GameState, action: Action) -> GameState | None:
        word = StringValue()
        if not action.payload.Unpack(word):
            return None
        standing = ScriptedRules._unpack_position(state.payload)
        advanced = ScriptedRules.position_payload(standing.position + 1, standing.participant_count)
        if word.value == MOVE:
            return self._get_turn_passed(advanced, action.participant, standing.participant_count)
        if word.value == WIN:
            return GameState(
                payload=advanced,
                participants_to_act=[],
                result=GameResult(
                    participant_items=[
                        ParticipantResult(
                            participant=number,
                            outcome=(
                                ParticipantOutcome.PARTICIPANT_OUTCOME_WON
                                if number == action.participant
                                else ParticipantOutcome.PARTICIPANT_OUTCOME_LOST
                            ),
                        )
                        for number in range(FIRST_PARTICIPANT, standing.participant_count + 1)
                    ]
                ),
            )
        return None

    async def withdraw_participant(self, state: GameState, participant: int) -> GameState | None:
        """
        A participant who leaves loses, and everyone else wins. A number the
        game was not created with is not in the game.
        """
        standing = ScriptedRules._unpack_position(state.payload)
        if not FIRST_PARTICIPANT <= participant <= standing.participant_count:
            return None
        return GameState(
            payload=ScriptedRules.position_payload(
                standing.position + 1, standing.participant_count
            ),
            participants_to_act=[],
            result=GameResult(
                participant_items=[
                    ParticipantResult(
                        participant=number,
                        outcome=(
                            ParticipantOutcome.PARTICIPANT_OUTCOME_LOST
                            if number == participant
                            else ParticipantOutcome.PARTICIPANT_OUTCOME_WON
                        ),
                    )
                    for number in range(FIRST_PARTICIPANT, standing.participant_count + 1)
                ]
            ),
        )

    async def expire_deadline(self, state: GameState) -> GameState | None:
        if not state.HasField("acts_within"):
            return None
        standing = ScriptedRules._unpack_position(state.payload)
        advanced = ScriptedRules.position_payload(standing.position + 1, standing.participant_count)
        return self._get_turn_passed(
            advanced, state.participants_to_act[0], standing.participant_count
        )

    async def read_view(self, state: GameState, participant: int) -> any_pb2.Any:
        standing = ScriptedRules._unpack_position(state.payload)
        return ScriptedRules.word_payload(f"{standing.position}{VIEW_SEPARATOR}{participant}")

    async def read_bounds(self) -> ParticipantBounds:
        return self._bounds

    def _get_turn_passed(
        self, advanced: any_pb2.Any, acting: int, participant_count: int
    ) -> GameState:
        """
        The state after `acting` took a turn: the next participant acts.
        """
        following = acting % participant_count + FIRST_PARTICIPANT
        return GameState(
            payload=advanced, participants_to_act=[following], acts_within=self._acts_within
        )

    @staticmethod
    def word_payload(word: str) -> any_pb2.Any:
        """
        An action, or a view, packed the way a client of this game packs one.
        """
        packed = any_pb2.Any()
        packed.Pack(StringValue(value=word))
        return packed

    @staticmethod
    def view_text(view: any_pb2.Any) -> str:
        """
        The word a view carries.
        """
        word = StringValue()
        assert view.Unpack(word)
        return word.value

    @staticmethod
    def position_payload(position: int, participant_count: int) -> any_pb2.Any:
        """
        The position and the size of the game, packed as one number each.
        """
        packed = any_pb2.Any()
        packed.Pack(UInt32Value(value=position * PARTICIPANT_COUNT_RADIX + participant_count))
        return packed

    @staticmethod
    def _unpack_position(payload: any_pb2.Any) -> ScriptedPosition:
        number = UInt32Value()
        assert payload.Unpack(number)
        position, participant_count = divmod(number.value, PARTICIPANT_COUNT_RADIX)
        return ScriptedPosition(position=position, participant_count=participant_count)
