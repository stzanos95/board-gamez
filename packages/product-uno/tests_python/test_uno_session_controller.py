import unittest

from game.controller.rules_registry import RulesRegistry
from game.controller.session_controller import SessionController
from idl.game.model.command_result_pb2 import CommandOutcome
from idl.game.model.game_type_pb2 import GameType
from idl.lobby.model.event_pb2 import SeatTaken, TableStarted
from idl.lobby.model.seat_pb2 import Seat, SeatStatus
from idl.lobby.model.seat_result_pb2 import SeatOutcome
from idl.lobby.model.table_pb2 import Table, TableStatus
from idl.uno.model.card_pb2 import CARD_COLOR_RED, CARD_COLOR_UNSPECIFIED
from idl.uno.model.game_pb2 import UNO_RESULT_REASON_OTHERS_WITHDREW
from idl.uno.model.session_pb2 import UnoSession
from idl.uno.model.table_pb2 import UnoSeatChoice
from lobby.controller.seat_controller import SeatController
from lobby.controller.seating_registry import SeatingRegistry
from lobby.controller.table_controller import TableController
from uno.core.cards import Cards
from uno.engine.uno_engine import HAND_SIZE

from product_uno.controller.uno_rules import UnoRules
from product_uno.controller.uno_seating import UnoSeating
from product_uno.controller.uno_session_controller import UnoSessionController
from tests_python.fixed_clock import FixedClock
from tests_python.in_memory_queue_publisher import InMemoryQueuePublisher
from tests_python.in_memory_repositories import InMemorySessionRepository, InMemoryTableRepository
from tests_python.uno_actions import draw, pass_turn, play

TABLE_ID = "t-1"
OPEN_TABLE_ID = "t-2"
OTHER_GAME_TABLE_ID = "t-3"
MISSING_TABLE_ID = "t-9"
FIRST_PLAYER = "p-1"
SECOND_PLAYER = "p-2"
THIRD_PLAYER = "p-3"
ONLOOKER = "p-4"
FIRST_SEAT = 1
SECOND_SEAT = 2
THIRD_SEAT = 3
NOT_PLAYING = 0
UNSTORED_VERSION = 0
FIRST_STORED_VERSION = 1
SECOND_STORED_VERSION = 2
UNO_SEAT_COUNT = 3
TOO_FEW_SEATS = 1
TABLE_CHANNEL = "table:t-1"
SESSION_CHANNEL = "session:t-1"
OPEN_TABLE_CHANNEL = "table:t-2"
LOBBY_CHANNEL = "lobby"
SEAT_TAKEN_TYPE = "idl.lobby.model.SeatTaken"
TABLE_STARTED_TYPE = "idl.lobby.model.TableStarted"
COMMAND_ID = "c-1"
PLAY_SEARCH_TURNS = 30
PLAYERS_BY_SEAT: dict[int, str] = {
    FIRST_SEAT: FIRST_PLAYER,
    SECOND_SEAT: SECOND_PLAYER,
    THIRD_SEAT: THIRD_PLAYER,
}
OTHER_COMMAND_ID = "c-2"


def occupied(number: int, player_id: str) -> Seat:
    return Seat(number=number, status=SeatStatus.SEAT_STATUS_OCCUPIED, player_id=player_id)


def open_seat(number: int) -> Seat:
    return Seat(number=number, status=SeatStatus.SEAT_STATUS_OPEN)


def require_session(session: UnoSession | None) -> UnoSession:
    assert session is not None
    return session


class UnoSessionControllerTest(unittest.IsolatedAsyncioTestCase):
    """
    Starting, reading and playing a game of UNO at a table, against stores
    kept in dictionaries.
    """

    async def asyncSetUp(self) -> None:
        self.queue_publisher = InMemoryQueuePublisher()
        self.tables = TableController(
            repository=InMemoryTableRepository(), queue_publisher=self.queue_publisher
        )
        rules = RulesRegistry({GameType.GAME_TYPE_UNO: UnoRules()})
        self.sessions = SessionController(
            repository=InMemorySessionRepository(),
            rules=rules,
            queue_publisher=self.queue_publisher,
            clock=FixedClock(),
        )
        self.seats = SeatController(
            tables=self.tables,
            seating=SeatingRegistry({GameType.GAME_TYPE_UNO: UnoSeating()}),
            sessions=self.sessions,
            rules=rules,
            queue_publisher=self.queue_publisher,
        )
        self.controller = UnoSessionController(
            tables=self.tables, seats=self.seats, sessions=self.sessions
        )
        await self.tables.upsert_table(
            Table(
                id=TABLE_ID,
                game_type=GameType.GAME_TYPE_UNO,
                status=TableStatus.TABLE_STATUS_WAITING,
                seats=[
                    occupied(FIRST_SEAT, FIRST_PLAYER),
                    occupied(SECOND_SEAT, SECOND_PLAYER),
                    occupied(THIRD_SEAT, THIRD_PLAYER),
                ],
                version=UNSTORED_VERSION,
                player_ids=[FIRST_PLAYER, SECOND_PLAYER, THIRD_PLAYER],
            )
        )
        await self.tables.upsert_table(
            Table(
                id=OPEN_TABLE_ID,
                game_type=GameType.GAME_TYPE_UNO,
                status=TableStatus.TABLE_STATUS_WAITING,
                seats=[
                    occupied(FIRST_SEAT, FIRST_PLAYER),
                    open_seat(SECOND_SEAT),
                    open_seat(THIRD_SEAT),
                ],
                version=UNSTORED_VERSION,
                player_ids=[FIRST_PLAYER],
            )
        )
        await self.tables.upsert_table(
            Table(
                id=OTHER_GAME_TABLE_ID,
                game_type=GameType.GAME_TYPE_UNSPECIFIED,
                status=TableStatus.TABLE_STATUS_WAITING,
                seats=[occupied(FIRST_SEAT, FIRST_PLAYER), occupied(SECOND_SEAT, SECOND_PLAYER)],
                version=UNSTORED_VERSION,
                player_ids=[FIRST_PLAYER, SECOND_PLAYER],
            )
        )

    async def start(self, player_id: str = FIRST_PLAYER, table_id: str = TABLE_ID) -> UnoSession:
        return require_session(await self.controller.start_game(table_id, player_id))

    async def test_a_seated_player_starts_the_game(self) -> None:
        session = await self.start()
        self.assertEqual(session.id, TABLE_ID)
        self.assertEqual(session.version, FIRST_STORED_VERSION)
        self.assertEqual(session.participant, FIRST_SEAT)
        self.assertEqual(len(session.view.hand), HAND_SIZE)
        self.assertEqual([player.participant for player in session.view.players], [1, 2, 3])
        self.assertEqual(session.view.participant_to_act, FIRST_SEAT)
        self.assertTrue(session.view.may_draw)

    async def test_the_third_seat_is_the_third_participant(self) -> None:
        session = await self.start(THIRD_PLAYER)
        self.assertEqual(session.participant, THIRD_SEAT)
        self.assertFalse(session.view.may_draw)

    async def test_an_onlooker_cannot_start_the_game(self) -> None:
        self.assertIsNone(await self.controller.start_game(TABLE_ID, ONLOOKER))

    async def test_a_table_with_an_open_seat_cannot_start(self) -> None:
        self.assertIsNone(await self.controller.start_game(OPEN_TABLE_ID, FIRST_PLAYER))

    async def test_a_table_of_another_game_cannot_start_uno(self) -> None:
        self.assertIsNone(await self.controller.start_game(OTHER_GAME_TABLE_ID, FIRST_PLAYER))

    async def test_a_missing_table_cannot_start(self) -> None:
        self.assertIsNone(await self.controller.start_game(MISSING_TABLE_ID, FIRST_PLAYER))

    async def test_starting_puts_the_table_in_progress(self) -> None:
        await self.start()
        table = await self.tables.read_table(TABLE_ID)
        assert table is not None
        self.assertEqual(table.status, TableStatus.TABLE_STATUS_IN_PROGRESS)
        self.assertEqual(table.version, SECOND_STORED_VERSION)

    async def test_starting_twice_answers_the_game_already_there(self) -> None:
        first = await self.start()
        again = await self.start(SECOND_PLAYER)
        self.assertEqual(again.version, first.version)
        self.assertEqual(again.participant, SECOND_SEAT)

    async def test_reading_before_a_game_starts_answers_nothing(self) -> None:
        self.assertIsNone(await self.controller.read_game(TABLE_ID, FIRST_PLAYER))

    async def test_an_onlooker_reads_the_game_without_a_hand(self) -> None:
        await self.start()
        session = require_session(await self.controller.read_game(TABLE_ID, ONLOOKER))
        self.assertEqual(session.participant, NOT_PLAYING)
        self.assertEqual(len(session.view.hand), 0)
        self.assertEqual([player.card_count for player in session.view.players], [7, 7, 7])

    async def test_each_player_reads_only_their_own_hand(self) -> None:
        await self.start()
        first = require_session(await self.controller.read_game(TABLE_ID, FIRST_PLAYER))
        second = require_session(await self.controller.read_game(TABLE_ID, SECOND_PLAYER))
        self.assertEqual(len(first.view.hand), HAND_SIZE)
        self.assertEqual(len(second.view.hand), HAND_SIZE)
        self.assertNotEqual(list(first.view.hand), list(second.view.hand))

    async def test_a_draw_and_a_pass_move_the_turn_on(self) -> None:
        session = await self.start()
        drawn = await self.controller.play_action(
            TABLE_ID, FIRST_PLAYER, COMMAND_ID, draw(), session.version
        )
        self.assertEqual(drawn.outcome, CommandOutcome.COMMAND_OUTCOME_APPLIED)
        self.assertEqual(drawn.session.version, SECOND_STORED_VERSION)
        self.assertEqual(drawn.session.last_command_id, COMMAND_ID)
        self.assertEqual(len(drawn.session.view.hand), HAND_SIZE + 1)
        self.assertTrue(drawn.session.view.may_pass)
        passed = await self.controller.play_action(
            TABLE_ID, FIRST_PLAYER, OTHER_COMMAND_ID, pass_turn(), drawn.session.version
        )
        self.assertEqual(passed.outcome, CommandOutcome.COMMAND_OUTCOME_APPLIED)
        self.assertEqual(passed.session.view.participant_to_act, SECOND_SEAT)

    async def test_the_platform_outcomes_come_through(self) -> None:
        session = await self.start()
        applied = await self.controller.play_action(
            TABLE_ID, FIRST_PLAYER, COMMAND_ID, draw(), session.version
        )
        repeated = await self.controller.play_action(
            TABLE_ID, FIRST_PLAYER, COMMAND_ID, draw(), session.version
        )
        self.assertEqual(repeated.outcome, CommandOutcome.COMMAND_OUTCOME_ALREADY_APPLIED)
        out_of_turn = await self.controller.play_action(
            TABLE_ID, SECOND_PLAYER, OTHER_COMMAND_ID, draw(), applied.session.version
        )
        self.assertEqual(out_of_turn.outcome, CommandOutcome.COMMAND_OUTCOME_OUT_OF_TURN)
        stale = await self.controller.play_action(
            TABLE_ID, FIRST_PLAYER, OTHER_COMMAND_ID, pass_turn(), session.version
        )
        self.assertEqual(stale.outcome, CommandOutcome.COMMAND_OUTCOME_VERSION_MOVED)
        illegal = await self.controller.play_action(
            TABLE_ID, FIRST_PLAYER, OTHER_COMMAND_ID, draw(), applied.session.version
        )
        self.assertEqual(illegal.outcome, CommandOutcome.COMMAND_OUTCOME_ILLEGAL_ACTION)
        onlooker = await self.controller.play_action(
            TABLE_ID, ONLOOKER, OTHER_COMMAND_ID, draw(), applied.session.version
        )
        self.assertEqual(onlooker.outcome, CommandOutcome.COMMAND_OUTCOME_NOT_A_PARTICIPANT)
        self.assertEqual(onlooker.session.participant, NOT_PLAYING)

    async def test_a_playable_card_from_the_view_is_accepted(self) -> None:
        """
        The deal is random, so the players draw and pass until one of them is
        shown a card they may play, and that card is played.
        """
        started = await self.start()
        to_act = started.view.participant_to_act
        for turn in range(PLAY_SEARCH_TURNS):
            actor = PLAYERS_BY_SEAT[to_act]
            session = require_session(await self.controller.read_game(TABLE_ID, actor))
            playable = [shown.card for shown in session.view.hand if shown.is_playable]
            if len(playable) > 0:
                chosen = CARD_COLOR_RED if Cards.is_wild(playable[0]) else CARD_COLOR_UNSPECIFIED
                result = await self.controller.play_action(
                    TABLE_ID, actor, f"c-{turn}", play(playable[0], chosen), session.version
                )
                self.assertEqual(result.outcome, CommandOutcome.COMMAND_OUTCOME_APPLIED)
                self.assertEqual(len(result.session.view.hand), len(session.view.hand) - 1)
                return
            drawn = await self.controller.play_action(
                TABLE_ID, actor, f"d-{turn}", draw(), session.version
            )
            self.assertEqual(drawn.outcome, CommandOutcome.COMMAND_OUTCOME_APPLIED)
            if drawn.session.view.hand[-1].is_playable:
                continue
            passed = await self.controller.play_action(
                TABLE_ID, actor, f"p-{turn}", pass_turn(), drawn.session.version
            )
            self.assertEqual(passed.outcome, CommandOutcome.COMMAND_OUTCOME_APPLIED)
            to_act = passed.session.view.participant_to_act
        self.fail("nobody was shown a playable card")

    async def test_playing_at_a_table_with_no_game_names_no_session(self) -> None:
        result = await self.controller.play_action(
            TABLE_ID, FIRST_PLAYER, COMMAND_ID, draw(), UNSTORED_VERSION
        )
        self.assertEqual(result.outcome, CommandOutcome.COMMAND_OUTCOME_SESSION_NOT_FOUND)
        self.assertFalse(result.HasField("session"))

    # --- seats ---------------------------------------------------------------

    async def test_every_open_seat_is_offered(self) -> None:
        choices = await self.controller.list_seat_choices(OPEN_TABLE_ID, ONLOOKER)
        self.assertEqual(
            list(choices.uno_seat_choice_items),
            [UnoSeatChoice(number=SECOND_SEAT), UnoSeatChoice(number=THIRD_SEAT)],
        )

    async def test_a_seated_player_is_offered_nothing(self) -> None:
        choices = await self.controller.list_seat_choices(OPEN_TABLE_ID, FIRST_PLAYER)
        self.assertEqual(len(choices.uno_seat_choice_items), 0)

    async def test_a_full_table_offers_nothing(self) -> None:
        choices = await self.controller.list_seat_choices(TABLE_ID, ONLOOKER)
        self.assertEqual(len(choices.uno_seat_choice_items), 0)

    async def test_taking_a_seat_seats_the_player_there(self) -> None:
        result = await self.controller.take_seat(
            OPEN_TABLE_ID, ONLOOKER, UnoSeatChoice(number=THIRD_SEAT), FIRST_STORED_VERSION
        )
        self.assertEqual(result.outcome, SeatOutcome.SEAT_OUTCOME_TAKEN)
        self.assertEqual(result.table.version, SECOND_STORED_VERSION)
        self.assertIn(ONLOOKER, result.table.player_ids)
        self.assertEqual(result.table.seats[THIRD_SEAT - 1].player_id, ONLOOKER)

    async def test_a_seat_that_is_taken_is_not_offered(self) -> None:
        result = await self.controller.take_seat(
            OPEN_TABLE_ID, ONLOOKER, UnoSeatChoice(number=FIRST_SEAT), FIRST_STORED_VERSION
        )
        self.assertEqual(result.outcome, SeatOutcome.SEAT_OUTCOME_NOT_OFFERED)

    async def test_a_choice_from_an_earlier_table_is_refused(self) -> None:
        result = await self.controller.take_seat(
            OPEN_TABLE_ID, ONLOOKER, UnoSeatChoice(number=SECOND_SEAT), UNSTORED_VERSION
        )
        self.assertEqual(result.outcome, SeatOutcome.SEAT_OUTCOME_VERSION_MOVED)

    async def test_a_missing_table_has_no_seat_to_take(self) -> None:
        result = await self.controller.take_seat(
            MISSING_TABLE_ID, ONLOOKER, UnoSeatChoice(number=FIRST_SEAT), UNSTORED_VERSION
        )
        self.assertEqual(result.outcome, SeatOutcome.SEAT_OUTCOME_TABLE_NOT_FOUND)
        self.assertFalse(result.HasField("table"))

    async def test_reading_the_table_shows_every_seat(self) -> None:
        table = await self.controller.read_table(TABLE_ID)
        assert table is not None
        self.assertEqual([seat.number for seat in table.seats], [1, 2, 3])
        self.assertIsNone(await self.controller.read_table(OTHER_GAME_TABLE_ID))

    # --- standing up ---------------------------------------------------------

    async def test_standing_up_mid_game_takes_the_player_out(self) -> None:
        started = await self.start()
        self.assertFalse(started.view.HasField("result"))

        result = await self.seats.vacate_seat(TABLE_ID, FIRST_PLAYER)

        self.assertEqual(result.outcome, SeatOutcome.SEAT_OUTCOME_VACATED)
        after = require_session(await self.controller.read_game(TABLE_ID, SECOND_PLAYER))
        self.assertTrue(after.view.players[FIRST_SEAT - 1].has_withdrawn)
        self.assertEqual(after.view.participant_to_act, SECOND_SEAT)
        self.assertFalse(after.view.HasField("result"))
        self.assertEqual(after.version, started.version + 1)

    async def test_the_last_player_left_wins(self) -> None:
        await self.start()
        await self.seats.vacate_seat(TABLE_ID, FIRST_PLAYER)
        await self.seats.leave_table(TABLE_ID, SECOND_PLAYER)
        after = require_session(await self.controller.read_game(TABLE_ID, THIRD_PLAYER))
        self.assertEqual(after.view.result.winner, THIRD_SEAT)
        self.assertEqual(after.view.result.reason, UNO_RESULT_REASON_OTHERS_WITHDREW)

    async def test_standing_up_before_a_game_only_opens_the_seat(self) -> None:
        result = await self.seats.vacate_seat(OPEN_TABLE_ID, FIRST_PLAYER)
        self.assertEqual(result.outcome, SeatOutcome.SEAT_OUTCOME_VACATED)
        self.assertIsNone(await self.controller.read_game(OPEN_TABLE_ID, FIRST_PLAYER))

    # --- opening a table -----------------------------------------------------

    async def test_a_uno_table_is_opened_with_the_seats_asked_for(self) -> None:
        result = await self.seats.create_table(GameType.GAME_TYPE_UNO, UNO_SEAT_COUNT, ONLOOKER)
        self.assertEqual(result.outcome, SeatOutcome.SEAT_OUTCOME_CREATED)
        self.assertEqual(len(result.table.seats), UNO_SEAT_COUNT)
        self.assertEqual(list(result.table.player_ids), [ONLOOKER])

    async def test_a_seat_count_uno_does_not_take_is_refused(self) -> None:
        result = await self.seats.create_table(GameType.GAME_TYPE_UNO, TOO_FEW_SEATS, ONLOOKER)
        self.assertEqual(result.outcome, SeatOutcome.SEAT_OUTCOME_SEAT_COUNT_NOT_ALLOWED)

    # --- publishing ----------------------------------------------------------

    async def test_taking_a_seat_is_published_on_the_table_and_the_lobby(self) -> None:
        result = await self.controller.take_seat(
            OPEN_TABLE_ID, ONLOOKER, UnoSeatChoice(number=SECOND_SEAT), FIRST_STORED_VERSION
        )
        self.assertEqual(self.queue_publisher.get_types_on(OPEN_TABLE_CHANNEL), [SEAT_TAKEN_TYPE])
        self.assertEqual(self.queue_publisher.get_types_on(LOBBY_CHANNEL), [SEAT_TAKEN_TYPE])
        taken = SeatTaken()
        self.assertTrue(self.queue_publisher.published[0].envelope.payload.Unpack(taken))
        self.assertEqual(taken.seat_number, SECOND_SEAT)
        self.assertEqual(taken.version, result.table.version)
        self.assertFalse(taken.HasField("role"))

    async def test_starting_is_published_on_the_session_the_table_and_the_lobby(self) -> None:
        await self.start()
        self.assertEqual(
            [published.channel for published in self.queue_publisher.published],
            [SESSION_CHANNEL, TABLE_CHANNEL, LOBBY_CHANNEL],
        )
        started = TableStarted()
        self.assertTrue(self.queue_publisher.published[-1].envelope.payload.Unpack(started))
        self.assertEqual(started.table_id, TABLE_ID)
        self.assertEqual(self.queue_publisher.get_types_on(LOBBY_CHANNEL), [TABLE_STARTED_TYPE])
