import unittest

from idl.game.model.command_result_pb2 import CommandOutcome, CommandResult
from idl.game.model.game_result_pb2 import ParticipantOutcome
from idl.game.model.game_type_pb2 import GameType
from idl.game.model.participant_pb2 import Participant
from idl.game.model.session_pb2 import SessionView

from game.controller.rules_registry import RulesRegistry
from game.controller.session_controller import SessionController
from tests_python.in_memory_session_repository import RefusingOnceSessionRepository
from tests_python.scripted_rules import MOVE, WIN, ScriptedRules

TABLE_ID = "t-1"
OTHER_TABLE_ID = "t-2"
FIRST_PLAYER = "p-1"
SECOND_PLAYER = "p-2"
ONLOOKER = "p-3"
FIRST_PARTICIPANT = 1
SECOND_PARTICIPANT = 2
NOBODY = 0
FIRST_STORED_VERSION = 1
SECOND_STORED_VERSION = 2
STALE_VERSION = 9
COMMAND_ID = "c-1"
OTHER_COMMAND_ID = "c-2"
NO_COMMAND_ID = ""
TWO_PLAYERS = (
    Participant(number=FIRST_PARTICIPANT, player_id=FIRST_PLAYER),
    Participant(number=SECOND_PARTICIPANT, player_id=SECOND_PLAYER),
)
ILLEGAL = "dance"


class SessionControllerTest(unittest.IsolatedAsyncioTestCase):
    """
    What each operation on a game means, against a scripted two-player game
    kept in a dictionary.
    """

    def setUp(self) -> None:
        self.repository = RefusingOnceSessionRepository()
        self.rules = ScriptedRules(minimum=2, maximum=2)
        self.controller = SessionController(
            repository=self.repository,
            rules=RulesRegistry({GameType.GAME_TYPE_CHESS: self.rules}),
        )
        self.commands_sent = 0

    async def start(self, player_id: str = FIRST_PLAYER) -> SessionView:
        """
        A game the test expects to start.
        """
        started = await self.controller.create_session(
            TABLE_ID, GameType.GAME_TYPE_CHESS, TWO_PLAYERS, player_id
        )
        assert started is not None
        return started

    async def apply(
        self,
        player_id: str,
        word: str,
        expected_version: int,
        command_id: str = COMMAND_ID,
    ) -> CommandResult:
        return await self.controller.apply_command(
            TABLE_ID,
            player_id,
            command_id,
            ScriptedRules.word_payload(word),
            expected_version,
        )

    async def applied(self, player_id: str, word: str, expected_version: int) -> SessionView:
        """
        A command the test expects to be applied, under an id of its own.
        """
        self.commands_sent += 1
        result = await self.apply(
            player_id, word, expected_version, command_id=f"{OTHER_COMMAND_ID}-{self.commands_sent}"
        )
        self.assertIs(result.outcome, CommandOutcome.COMMAND_OUTCOME_APPLIED)
        return result.session

    # --- starting a game -------------------------------------------------------

    async def test_a_new_game_is_stored_at_the_first_version_with_the_first_to_act(self) -> None:
        started = await self.start()

        self.assertEqual(started.id, TABLE_ID)
        self.assertEqual(started.version, FIRST_STORED_VERSION)
        self.assertEqual(started.state.participant_to_act, FIRST_PARTICIPANT)
        self.assertFalse(started.state.HasField("result"))
        self.assertEqual(started.last_command_id, NO_COMMAND_ID)
        self.assertEqual(list(started.participants), list(TWO_PLAYERS))

    async def test_a_game_is_answered_as_the_caller_may_see_it(self) -> None:
        started = await self.start(player_id=SECOND_PLAYER)

        self.assertEqual(started.participant, SECOND_PARTICIPANT)
        self.assertEqual(ScriptedRules.view_text(started.state.payload), "0:2")

    async def test_starting_a_game_at_a_table_already_playing_one_answers_that_game(self) -> None:
        first = await self.start(player_id=FIRST_PLAYER)
        again = await self.start(player_id=SECOND_PLAYER)

        self.assertEqual(again.version, first.version)
        self.assertEqual(again.participant, SECOND_PARTICIPANT)

    async def test_a_roster_the_game_does_not_take_starts_nothing(self) -> None:
        one_player = (Participant(number=FIRST_PARTICIPANT, player_id=FIRST_PLAYER),)

        started = await self.controller.create_session(
            TABLE_ID, GameType.GAME_TYPE_CHESS, one_player, FIRST_PLAYER
        )

        self.assertIsNone(started)
        self.assertIsNone(await self.repository.read(TABLE_ID))

    async def test_a_roster_with_a_gap_in_its_numbering_starts_nothing(self) -> None:
        gapped = (
            Participant(number=FIRST_PARTICIPANT, player_id=FIRST_PLAYER),
            Participant(number=SECOND_PARTICIPANT + 1, player_id=SECOND_PLAYER),
        )

        started = await self.controller.create_session(
            TABLE_ID, GameType.GAME_TYPE_CHESS, gapped, FIRST_PLAYER
        )

        self.assertIsNone(started)

    async def test_a_start_whose_write_is_refused_answers_what_is_stored(self) -> None:
        self.repository.refuse_next_write = True

        started = await self.controller.create_session(
            TABLE_ID, GameType.GAME_TYPE_CHESS, TWO_PLAYERS, FIRST_PLAYER
        )

        # Nothing else wrote here, so the refused write finds no game to answer.
        self.assertIsNone(started)

    async def test_a_game_of_an_unconfigured_type_is_a_bringup_error(self) -> None:
        with self.assertRaises(RuntimeError):
            await self.controller.create_session(
                TABLE_ID, GameType.GAME_TYPE_UNSPECIFIED, TWO_PLAYERS, FIRST_PLAYER
            )

    # --- reading a game --------------------------------------------------------

    async def test_reading_a_game_that_is_not_there_answers_nothing(self) -> None:
        self.assertIsNone(await self.controller.read_session(OTHER_TABLE_ID, FIRST_PLAYER))

    async def test_someone_not_playing_reads_the_game_as_nobody(self) -> None:
        await self.start()

        seen = await self.controller.read_session(TABLE_ID, ONLOOKER)

        assert seen is not None
        self.assertEqual(seen.participant, NOBODY)
        self.assertEqual(ScriptedRules.view_text(seen.state.payload), "0:0")

    # --- applying a command, one outcome at a time -----------------------------

    async def test_a_command_to_a_game_that_is_not_there_is_not_found(self) -> None:
        result = await self.apply(FIRST_PLAYER, MOVE, FIRST_STORED_VERSION)

        self.assertIs(result.outcome, CommandOutcome.COMMAND_OUTCOME_SESSION_NOT_FOUND)
        self.assertFalse(result.HasField("session"))

    async def test_a_legal_command_in_turn_is_applied(self) -> None:
        await self.start()

        result = await self.apply(FIRST_PLAYER, MOVE, FIRST_STORED_VERSION)

        self.assertIs(result.outcome, CommandOutcome.COMMAND_OUTCOME_APPLIED)
        self.assertEqual(result.session.version, SECOND_STORED_VERSION)
        self.assertEqual(result.session.state.participant_to_act, SECOND_PARTICIPANT)
        self.assertEqual(result.session.last_command_id, COMMAND_ID)
        self.assertEqual(ScriptedRules.view_text(result.session.state.payload), "1:1")

    async def test_the_same_command_again_applies_nothing_and_answers_what_it_produced(
        self,
    ) -> None:
        await self.start()
        first = await self.apply(FIRST_PLAYER, MOVE, FIRST_STORED_VERSION)

        # A retry carries the version the command was first sent with.
        again = await self.apply(FIRST_PLAYER, MOVE, FIRST_STORED_VERSION)

        self.assertIs(again.outcome, CommandOutcome.COMMAND_OUTCOME_ALREADY_APPLIED)
        self.assertEqual(again.session.version, first.session.version)

    async def test_an_empty_command_id_is_never_a_repeat(self) -> None:
        await self.start()
        await self.apply(FIRST_PLAYER, MOVE, FIRST_STORED_VERSION, command_id=NO_COMMAND_ID)

        result = await self.apply(
            SECOND_PLAYER, MOVE, SECOND_STORED_VERSION, command_id=NO_COMMAND_ID
        )

        self.assertIs(result.outcome, CommandOutcome.COMMAND_OUTCOME_APPLIED)

    async def test_someone_not_playing_cannot_act(self) -> None:
        await self.start()

        result = await self.apply(ONLOOKER, MOVE, FIRST_STORED_VERSION)

        self.assertIs(result.outcome, CommandOutcome.COMMAND_OUTCOME_NOT_A_PARTICIPANT)
        self.assertEqual(result.session.participant, NOBODY)

    async def test_a_command_built_on_an_earlier_version_is_refused(self) -> None:
        await self.start()

        result = await self.apply(FIRST_PLAYER, MOVE, STALE_VERSION)

        self.assertIs(result.outcome, CommandOutcome.COMMAND_OUTCOME_VERSION_MOVED)
        self.assertEqual(result.session.version, FIRST_STORED_VERSION)

    async def test_acting_out_of_turn_is_refused(self) -> None:
        await self.start()

        result = await self.apply(SECOND_PLAYER, MOVE, FIRST_STORED_VERSION)

        self.assertIs(result.outcome, CommandOutcome.COMMAND_OUTCOME_OUT_OF_TURN)

    async def test_a_second_command_in_the_same_turn_is_out_of_turn(self) -> None:
        await self.start()
        moved = await self.applied(FIRST_PLAYER, MOVE, FIRST_STORED_VERSION)

        result = await self.apply(FIRST_PLAYER, MOVE, moved.version)

        self.assertIs(result.outcome, CommandOutcome.COMMAND_OUTCOME_OUT_OF_TURN)

    async def test_an_action_the_rules_refuse_is_illegal(self) -> None:
        await self.start()

        result = await self.apply(FIRST_PLAYER, ILLEGAL, FIRST_STORED_VERSION)

        self.assertIs(result.outcome, CommandOutcome.COMMAND_OUTCOME_ILLEGAL_ACTION)
        self.assertEqual(result.session.version, FIRST_STORED_VERSION)

    async def test_a_game_with_a_result_takes_no_more_commands(self) -> None:
        await self.start()
        won = await self.applied(FIRST_PLAYER, WIN, FIRST_STORED_VERSION)

        self.assertEqual(won.state.participant_to_act, NOBODY)
        outcomes = {one.participant: one.outcome for one in won.state.result.participant_items}
        self.assertIs(outcomes[FIRST_PARTICIPANT], ParticipantOutcome.PARTICIPANT_OUTCOME_WON)
        self.assertIs(outcomes[SECOND_PARTICIPANT], ParticipantOutcome.PARTICIPANT_OUTCOME_LOST)

        result = await self.apply(SECOND_PLAYER, MOVE, won.version)

        self.assertIs(result.outcome, CommandOutcome.COMMAND_OUTCOME_GAME_OVER)

    async def test_a_write_the_store_refuses_answers_the_version_that_moved(self) -> None:
        await self.start()
        self.repository.refuse_next_write = True

        result = await self.apply(FIRST_PLAYER, MOVE, FIRST_STORED_VERSION)

        self.assertIs(result.outcome, CommandOutcome.COMMAND_OUTCOME_VERSION_MOVED)
        self.assertEqual(result.session.version, FIRST_STORED_VERSION)

    async def test_turns_alternate_across_a_whole_exchange(self) -> None:
        started = await self.start()
        first = await self.applied(FIRST_PLAYER, MOVE, started.version)
        second = await self.applied(SECOND_PLAYER, MOVE, first.version)
        third = await self.applied(FIRST_PLAYER, MOVE, second.version)

        self.assertEqual(third.state.participant_to_act, SECOND_PARTICIPANT)
        self.assertEqual(third.version, started.version + 3)
        self.assertEqual(ScriptedRules.view_text(third.state.payload), "3:1")
