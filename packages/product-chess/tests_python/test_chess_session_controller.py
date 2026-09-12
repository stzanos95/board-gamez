import unittest

from game.controller.rules_registry import RulesRegistry
from game.controller.session_controller import SessionController
from idl.chess.model import game_pb2, piece_pb2
from idl.chess.model.session_pb2 import ChessSession
from idl.chess.model.table_pb2 import ChessSeatChoice
from idl.game.model.command_result_pb2 import CommandOutcome
from idl.game.model.game_type_pb2 import GameType
from idl.lobby.model.event_pb2 import PlayerLeft, SeatTaken, SeatVacated
from idl.lobby.model.seat_pb2 import Seat, SeatStatus
from idl.lobby.model.seat_result_pb2 import SeatOutcome
from idl.lobby.model.table_pb2 import Table, TableStatus
from lobby.controller.seat_controller import SeatController
from lobby.controller.seating_registry import SeatingRegistry
from lobby.controller.table_controller import TableController

from product_chess.adapters.chess_seat_adapters import ChessSeatAdapters
from product_chess.controller.chess_rules import ChessRules
from product_chess.controller.chess_seating import ChessSeating
from product_chess.controller.chess_session_controller import ChessSessionController
from tests_python.chess_actions import move, resignation
from tests_python.in_memory_queue_publisher import InMemoryQueuePublisher
from tests_python.in_memory_repositories import InMemorySessionRepository, InMemoryTableRepository

TABLE_ID = "t-1"
EMPTY_TABLE_ID = "t-2"
OTHER_GAME_TABLE_ID = "t-3"
MISSING_TABLE_ID = "t-9"
WHITE_PLAYER = "p-1"
BLACK_PLAYER = "p-2"
ONLOOKER = "p-3"
FIRST_SEAT = 1
SECOND_SEAT = 2
UNSTORED_VERSION = 0
FIRST_STORED_VERSION = 1
SECOND_STORED_VERSION = 2
CHESS_SEAT_COUNT = 2
NO_SEAT = 0
TABLE_CHANNEL = "table:t-1"
SESSION_CHANNEL = "session:t-1"
EMPTY_TABLE_CHANNEL = "table:t-2"
LOBBY_CHANNEL = "lobby"
SEAT_TAKEN_TYPE = "idl.lobby.model.SeatTaken"
SEAT_VACATED_TYPE = "idl.lobby.model.SeatVacated"
PARTICIPANT_WITHDRAWN_TYPE = "idl.game.model.ParticipantWithdrawn"
TABLE_CREATED_TYPE = "idl.lobby.model.TableCreated"
PLAYER_JOINED_TYPE = "idl.lobby.model.PlayerJoined"
PLAYER_LEFT_TYPE = "idl.lobby.model.PlayerLeft"
COMMAND_ID = "c-1"
OTHER_COMMAND_ID = "c-2"


def occupied(number: int, player_id: str) -> Seat:
    return Seat(
        number=number,
        status=SeatStatus.SEAT_STATUS_OCCUPIED,
        player_id=player_id,
        role=ChessSeatAdapters.color_to_role(ChessSeatAdapters.seat_number_to_color(number)),
    )


def open_seat(number: int) -> Seat:
    return Seat(number=number, status=SeatStatus.SEAT_STATUS_OPEN)


def require_session(session: ChessSession | None) -> ChessSession:
    assert session is not None
    return session


class ChessSessionControllerTest(unittest.IsolatedAsyncioTestCase):
    """
    Starting, reading and playing a game of chess at a table, against stores
    kept in dictionaries.
    """

    async def asyncSetUp(self) -> None:
        self.queue_publisher = InMemoryQueuePublisher()
        self.tables = TableController(
            repository=InMemoryTableRepository(), queue_publisher=self.queue_publisher
        )
        rules = RulesRegistry({GameType.GAME_TYPE_CHESS: ChessRules()})
        self.sessions = SessionController(
            repository=InMemorySessionRepository(),
            rules=rules,
            queue_publisher=self.queue_publisher,
        )
        self.seats = SeatController(
            tables=self.tables,
            seating=SeatingRegistry({GameType.GAME_TYPE_CHESS: ChessSeating()}),
            sessions=self.sessions,
            rules=rules,
            queue_publisher=self.queue_publisher,
        )
        self.controller = ChessSessionController(
            tables=self.tables, seats=self.seats, sessions=self.sessions
        )
        await self.tables.upsert_table(
            Table(
                id=TABLE_ID,
                game_type=GameType.GAME_TYPE_CHESS,
                status=TableStatus.TABLE_STATUS_WAITING,
                seats=[occupied(FIRST_SEAT, WHITE_PLAYER), occupied(SECOND_SEAT, BLACK_PLAYER)],
                version=UNSTORED_VERSION,
                player_ids=[WHITE_PLAYER, BLACK_PLAYER],
            )
        )
        await self.tables.upsert_table(
            Table(
                id=EMPTY_TABLE_ID,
                game_type=GameType.GAME_TYPE_CHESS,
                status=TableStatus.TABLE_STATUS_WAITING,
                seats=[occupied(FIRST_SEAT, WHITE_PLAYER), open_seat(SECOND_SEAT)],
                version=UNSTORED_VERSION,
                player_ids=[WHITE_PLAYER],
            )
        )
        await self.tables.upsert_table(
            Table(
                id=OTHER_GAME_TABLE_ID,
                game_type=GameType.GAME_TYPE_UNSPECIFIED,
                status=TableStatus.TABLE_STATUS_WAITING,
                seats=[occupied(FIRST_SEAT, WHITE_PLAYER), occupied(SECOND_SEAT, BLACK_PLAYER)],
                version=UNSTORED_VERSION,
                player_ids=[WHITE_PLAYER, BLACK_PLAYER],
            )
        )

    async def start(self, player_id: str = WHITE_PLAYER, table_id: str = TABLE_ID) -> ChessSession:
        return require_session(await self.controller.start_game(table_id, player_id))

    async def test_a_seated_player_starts_the_game(self) -> None:
        session = await self.start()
        self.assertEqual(session.id, TABLE_ID)
        self.assertEqual(session.version, FIRST_STORED_VERSION)
        self.assertEqual(session.color, piece_pb2.COLOR_WHITE)
        self.assertEqual(session.game.roster.white.participant, FIRST_SEAT)
        self.assertEqual(session.game.roster.black.participant, SECOND_SEAT)
        self.assertEqual(len(session.game.legal_moves), 20)

    async def test_the_second_seat_plays_black(self) -> None:
        session = await self.start(BLACK_PLAYER)
        self.assertEqual(session.color, piece_pb2.COLOR_BLACK)

    async def test_an_onlooker_cannot_start_the_game(self) -> None:
        self.assertIsNone(await self.controller.start_game(TABLE_ID, ONLOOKER))

    async def test_a_table_with_an_open_seat_cannot_start(self) -> None:
        self.assertIsNone(await self.controller.start_game(EMPTY_TABLE_ID, WHITE_PLAYER))

    async def test_a_table_of_another_game_cannot_start_chess(self) -> None:
        self.assertIsNone(await self.controller.start_game(OTHER_GAME_TABLE_ID, WHITE_PLAYER))

    async def test_a_missing_table_cannot_start(self) -> None:
        self.assertIsNone(await self.controller.start_game(MISSING_TABLE_ID, WHITE_PLAYER))

    async def test_starting_twice_answers_the_game_already_there(self) -> None:
        first = await self.start()
        again = await self.start(BLACK_PLAYER)
        self.assertEqual(again.version, first.version)
        self.assertEqual(again.color, piece_pb2.COLOR_BLACK)

    async def test_reading_before_a_game_starts_answers_nothing(self) -> None:
        self.assertIsNone(await self.controller.read_game(TABLE_ID, WHITE_PLAYER))

    async def test_an_onlooker_reads_the_game_without_a_colour(self) -> None:
        await self.start()
        session = require_session(await self.controller.read_game(TABLE_ID, ONLOOKER))
        self.assertEqual(session.color, piece_pb2.COLOR_UNSPECIFIED)
        self.assertEqual(len(session.game.state.occupancy), 32)

    async def test_a_move_is_applied_and_the_turn_passes(self) -> None:
        session = await self.start()
        result = await self.controller.play_action(
            TABLE_ID, WHITE_PLAYER, COMMAND_ID, move("e2e4"), session.version
        )
        self.assertEqual(result.outcome, CommandOutcome.COMMAND_OUTCOME_APPLIED)
        self.assertEqual(result.session.version, SECOND_STORED_VERSION)
        self.assertEqual(result.session.last_command_id, COMMAND_ID)
        self.assertEqual(result.session.game.state.side_to_move, piece_pb2.COLOR_BLACK)
        self.assertEqual(result.session.game.history.turns[0].notation, "e4")

    async def test_the_platform_outcomes_come_through(self) -> None:
        session = await self.start()
        applied = await self.controller.play_action(
            TABLE_ID, WHITE_PLAYER, COMMAND_ID, move("e2e4"), session.version
        )
        repeated = await self.controller.play_action(
            TABLE_ID, WHITE_PLAYER, COMMAND_ID, move("e2e4"), session.version
        )
        self.assertEqual(repeated.outcome, CommandOutcome.COMMAND_OUTCOME_ALREADY_APPLIED)
        out_of_turn = await self.controller.play_action(
            TABLE_ID, WHITE_PLAYER, OTHER_COMMAND_ID, move("d2d4"), applied.session.version
        )
        self.assertEqual(out_of_turn.outcome, CommandOutcome.COMMAND_OUTCOME_OUT_OF_TURN)
        stale = await self.controller.play_action(
            TABLE_ID, BLACK_PLAYER, OTHER_COMMAND_ID, move("e7e5"), session.version
        )
        self.assertEqual(stale.outcome, CommandOutcome.COMMAND_OUTCOME_VERSION_MOVED)
        illegal = await self.controller.play_action(
            TABLE_ID, BLACK_PLAYER, OTHER_COMMAND_ID, move("e7e3"), applied.session.version
        )
        self.assertEqual(illegal.outcome, CommandOutcome.COMMAND_OUTCOME_ILLEGAL_ACTION)
        onlooker = await self.controller.play_action(
            TABLE_ID, ONLOOKER, OTHER_COMMAND_ID, move("e7e5"), applied.session.version
        )
        self.assertEqual(onlooker.outcome, CommandOutcome.COMMAND_OUTCOME_NOT_A_PARTICIPANT)
        self.assertEqual(onlooker.session.color, piece_pb2.COLOR_UNSPECIFIED)

    async def test_playing_at_a_table_with_no_game_names_no_session(self) -> None:
        result = await self.controller.play_action(
            TABLE_ID, WHITE_PLAYER, COMMAND_ID, move("e2e4"), UNSTORED_VERSION
        )
        self.assertEqual(result.outcome, CommandOutcome.COMMAND_OUTCOME_SESSION_NOT_FOUND)
        self.assertFalse(result.HasField("session"))

    async def test_resigning_ends_the_game(self) -> None:
        session = await self.start()
        resigned = await self.controller.play_action(
            TABLE_ID, WHITE_PLAYER, COMMAND_ID, resignation(), session.version
        )
        self.assertEqual(resigned.outcome, CommandOutcome.COMMAND_OUTCOME_APPLIED)
        self.assertEqual(resigned.session.game.resigning_color, piece_pb2.COLOR_WHITE)
        after = await self.controller.play_action(
            TABLE_ID, BLACK_PLAYER, OTHER_COMMAND_ID, move("e7e5"), resigned.session.version
        )
        self.assertEqual(after.outcome, CommandOutcome.COMMAND_OUTCOME_GAME_OVER)

    # --- seats ---------------------------------------------------------------

    async def test_the_open_seat_is_offered_with_its_side(self) -> None:
        choices = await self.controller.list_seat_choices(EMPTY_TABLE_ID, ONLOOKER)
        self.assertEqual(
            list(choices.chess_seat_choice_items),
            [ChessSeatChoice(number=SECOND_SEAT, color=piece_pb2.COLOR_BLACK)],
        )

    async def test_a_seated_player_is_offered_nothing(self) -> None:
        choices = await self.controller.list_seat_choices(EMPTY_TABLE_ID, WHITE_PLAYER)
        self.assertEqual(len(choices.chess_seat_choice_items), 0)

    async def test_a_full_table_offers_nothing(self) -> None:
        choices = await self.controller.list_seat_choices(TABLE_ID, ONLOOKER)
        self.assertEqual(len(choices.chess_seat_choice_items), 0)

    async def test_taking_the_open_seat_seats_the_player_as_black(self) -> None:
        result = await self.controller.take_seat(
            EMPTY_TABLE_ID,
            ONLOOKER,
            ChessSeatChoice(number=SECOND_SEAT, color=piece_pb2.COLOR_BLACK),
            FIRST_STORED_VERSION,
        )
        self.assertEqual(result.outcome, SeatOutcome.SEAT_OUTCOME_TAKEN)
        self.assertEqual(result.table.version, SECOND_STORED_VERSION)
        self.assertIn(ONLOOKER, result.table.player_ids)
        taken = result.table.seats[SECOND_SEAT - 1]
        self.assertEqual(taken.player_id, ONLOOKER)
        self.assertEqual(taken.color, piece_pb2.COLOR_BLACK)
        session = await self.start(ONLOOKER, EMPTY_TABLE_ID)
        self.assertEqual(session.color, piece_pb2.COLOR_BLACK)

    async def test_a_side_the_seat_does_not_play_is_not_offered(self) -> None:
        result = await self.controller.take_seat(
            EMPTY_TABLE_ID,
            ONLOOKER,
            ChessSeatChoice(number=SECOND_SEAT, color=piece_pb2.COLOR_WHITE),
            FIRST_STORED_VERSION,
        )
        self.assertEqual(result.outcome, SeatOutcome.SEAT_OUTCOME_NOT_OFFERED)
        self.assertEqual(result.table.version, FIRST_STORED_VERSION)

    async def test_a_choice_from_an_earlier_table_is_refused(self) -> None:
        result = await self.controller.take_seat(
            EMPTY_TABLE_ID,
            ONLOOKER,
            ChessSeatChoice(number=SECOND_SEAT, color=piece_pb2.COLOR_BLACK),
            UNSTORED_VERSION,
        )
        self.assertEqual(result.outcome, SeatOutcome.SEAT_OUTCOME_VERSION_MOVED)

    async def test_a_missing_table_has_no_seat_to_take(self) -> None:
        result = await self.controller.take_seat(
            MISSING_TABLE_ID,
            ONLOOKER,
            ChessSeatChoice(number=FIRST_SEAT, color=piece_pb2.COLOR_WHITE),
            UNSTORED_VERSION,
        )
        self.assertEqual(result.outcome, SeatOutcome.SEAT_OUTCOME_TABLE_NOT_FOUND)
        self.assertFalse(result.HasField("table"))

    async def test_reading_the_table_opens_every_side(self) -> None:
        table = await self.controller.read_table(TABLE_ID)
        assert table is not None
        self.assertEqual(
            [seat.color for seat in table.seats], [piece_pb2.COLOR_WHITE, piece_pb2.COLOR_BLACK]
        )
        self.assertIsNone(await self.controller.read_table(OTHER_GAME_TABLE_ID))

    # --- standing up ---------------------------------------------------------

    async def test_standing_up_mid_game_resigns_and_the_other_side_wins(self) -> None:
        started = await self.start()
        self.assertFalse(started.game.HasField("result"))

        result = await self.seats.vacate_seat(TABLE_ID, BLACK_PLAYER)

        self.assertEqual(result.outcome, SeatOutcome.SEAT_OUTCOME_VACATED)
        self.assertEqual(result.table.seats[SECOND_SEAT - 1].status, SeatStatus.SEAT_STATUS_OPEN)
        self.assertIn(BLACK_PLAYER, result.table.player_ids)
        after = await self.controller.read_game(TABLE_ID, WHITE_PLAYER)
        assert after is not None
        self.assertEqual(after.game.resigning_color, piece_pb2.COLOR_BLACK)
        self.assertEqual(after.game.result.outcome, game_pb2.GAME_OUTCOME_WHITE_WINS)
        self.assertEqual(after.version, started.version + 1)

    async def test_standing_up_out_of_turn_still_resigns(self) -> None:
        started = await self.start()
        self.assertEqual(started.game.state.side_to_move, piece_pb2.COLOR_WHITE)

        result = await self.seats.vacate_seat(TABLE_ID, BLACK_PLAYER)

        self.assertEqual(result.outcome, SeatOutcome.SEAT_OUTCOME_VACATED)
        after = await self.controller.read_game(TABLE_ID, WHITE_PLAYER)
        assert after is not None
        self.assertEqual(after.game.resigning_color, piece_pb2.COLOR_BLACK)

    async def test_leaving_the_table_mid_game_resigns_and_removes_the_player(self) -> None:
        await self.start()

        result = await self.seats.leave_table(TABLE_ID, WHITE_PLAYER)

        self.assertEqual(result.outcome, SeatOutcome.SEAT_OUTCOME_LEFT)
        self.assertNotIn(WHITE_PLAYER, result.table.player_ids)
        after = await self.controller.read_game(TABLE_ID, BLACK_PLAYER)
        assert after is not None
        self.assertEqual(after.game.result.outcome, game_pb2.GAME_OUTCOME_BLACK_WINS)

    async def test_standing_up_before_a_game_only_opens_the_seat(self) -> None:
        result = await self.seats.vacate_seat(EMPTY_TABLE_ID, WHITE_PLAYER)

        self.assertEqual(result.outcome, SeatOutcome.SEAT_OUTCOME_VACATED)
        self.assertIsNone(await self.controller.read_game(EMPTY_TABLE_ID, WHITE_PLAYER))

    async def test_standing_up_after_the_game_is_over_leaves_the_result(self) -> None:
        session = await self.start()
        resigned = await self.controller.play_action(
            TABLE_ID, WHITE_PLAYER, COMMAND_ID, resignation(), session.version
        )

        result = await self.seats.vacate_seat(TABLE_ID, BLACK_PLAYER)

        self.assertEqual(result.outcome, SeatOutcome.SEAT_OUTCOME_VACATED)
        after = await self.controller.read_game(TABLE_ID, WHITE_PLAYER)
        assert after is not None
        self.assertEqual(after.version, resigned.session.version)
        self.assertEqual(after.game.resigning_color, piece_pb2.COLOR_WHITE)

    async def test_someone_without_a_seat_cannot_stand_up(self) -> None:
        result = await self.seats.vacate_seat(TABLE_ID, ONLOOKER)
        self.assertEqual(result.outcome, SeatOutcome.SEAT_OUTCOME_NOT_SEATED)

    async def test_someone_not_at_the_table_cannot_leave_it(self) -> None:
        result = await self.seats.leave_table(TABLE_ID, ONLOOKER)
        self.assertEqual(result.outcome, SeatOutcome.SEAT_OUTCOME_NOT_AT_TABLE)

    # --- opening and joining a table -----------------------------------------

    async def test_a_chess_table_is_opened_with_two_open_seats(self) -> None:
        result = await self.seats.create_table(GameType.GAME_TYPE_CHESS, CHESS_SEAT_COUNT, ONLOOKER)
        self.assertEqual(result.outcome, SeatOutcome.SEAT_OUTCOME_CREATED)
        self.assertTrue(result.table.id)
        self.assertEqual(result.table.version, FIRST_STORED_VERSION)
        self.assertEqual(result.table.status, TableStatus.TABLE_STATUS_WAITING)
        self.assertEqual(list(result.table.player_ids), [ONLOOKER])
        self.assertEqual(list(result.table.seats), [open_seat(FIRST_SEAT), open_seat(SECOND_SEAT)])
        stored = await self.tables.read_table(result.table.id)
        self.assertEqual(stored, result.table)

    async def test_every_opened_table_has_its_own_id(self) -> None:
        first = await self.seats.create_table(GameType.GAME_TYPE_CHESS, CHESS_SEAT_COUNT, ONLOOKER)
        second = await self.seats.create_table(GameType.GAME_TYPE_CHESS, CHESS_SEAT_COUNT, ONLOOKER)
        self.assertNotEqual(first.table.id, second.table.id)

    async def test_a_seat_count_chess_does_not_take_is_refused(self) -> None:
        result = await self.seats.create_table(
            GameType.GAME_TYPE_CHESS, CHESS_SEAT_COUNT + 1, ONLOOKER
        )
        self.assertEqual(result.outcome, SeatOutcome.SEAT_OUTCOME_SEAT_COUNT_NOT_ALLOWED)
        self.assertFalse(result.HasField("table"))

    async def test_a_game_this_process_does_not_host_is_refused(self) -> None:
        result = await self.seats.create_table(
            GameType.GAME_TYPE_UNSPECIFIED, CHESS_SEAT_COUNT, ONLOOKER
        )
        self.assertEqual(result.outcome, SeatOutcome.SEAT_OUTCOME_GAME_NOT_HOSTED)

    async def test_the_opened_table_seats_its_opener_through_the_game(self) -> None:
        opened = await self.seats.create_table(GameType.GAME_TYPE_CHESS, CHESS_SEAT_COUNT, ONLOOKER)
        choices = await self.controller.list_seat_choices(opened.table.id, ONLOOKER)
        self.assertEqual(len(choices.chess_seat_choice_items), CHESS_SEAT_COUNT)
        taken = await self.controller.take_seat(
            opened.table.id,
            ONLOOKER,
            ChessSeatChoice(number=FIRST_SEAT, color=piece_pb2.COLOR_WHITE),
            opened.table.version,
        )
        self.assertEqual(taken.outcome, SeatOutcome.SEAT_OUTCOME_TAKEN)
        self.assertEqual(list(taken.table.player_ids), [ONLOOKER])

    async def test_joining_puts_the_player_at_the_table_without_a_seat(self) -> None:
        result = await self.seats.join_table(EMPTY_TABLE_ID, ONLOOKER)
        self.assertEqual(result.outcome, SeatOutcome.SEAT_OUTCOME_JOINED)
        self.assertEqual(result.table.version, SECOND_STORED_VERSION)
        self.assertEqual(list(result.table.player_ids), [WHITE_PLAYER, ONLOOKER])
        self.assertEqual(result.table.seats[SECOND_SEAT - 1], open_seat(SECOND_SEAT))

    async def test_joining_twice_is_refused_with_the_table(self) -> None:
        result = await self.seats.join_table(EMPTY_TABLE_ID, WHITE_PLAYER)
        self.assertEqual(result.outcome, SeatOutcome.SEAT_OUTCOME_ALREADY_AT_TABLE)
        self.assertEqual(result.table.version, FIRST_STORED_VERSION)

    async def test_joining_a_missing_table_names_no_table(self) -> None:
        result = await self.seats.join_table(MISSING_TABLE_ID, ONLOOKER)
        self.assertEqual(result.outcome, SeatOutcome.SEAT_OUTCOME_TABLE_NOT_FOUND)
        self.assertFalse(result.HasField("table"))

    async def test_a_finished_table_takes_nobody(self) -> None:
        table = await self.tables.read_table(EMPTY_TABLE_ID)
        assert table is not None
        table.status = TableStatus.TABLE_STATUS_FINISHED
        await self.tables.upsert_table(table)
        result = await self.seats.join_table(EMPTY_TABLE_ID, ONLOOKER)
        self.assertEqual(result.outcome, SeatOutcome.SEAT_OUTCOME_NOT_ACCEPTING_PLAYERS)
        self.assertNotIn(ONLOOKER, result.table.player_ids)

    # --- publishing ----------------------------------------------------------

    async def test_taking_a_seat_is_published_on_the_table_and_the_lobby(self) -> None:
        result = await self.controller.take_seat(
            EMPTY_TABLE_ID,
            ONLOOKER,
            ChessSeatChoice(number=SECOND_SEAT, color=piece_pb2.COLOR_BLACK),
            FIRST_STORED_VERSION,
        )
        self.assertEqual(self.queue_publisher.get_types_on(EMPTY_TABLE_CHANNEL), [SEAT_TAKEN_TYPE])
        self.assertEqual(self.queue_publisher.get_types_on(LOBBY_CHANNEL), [SEAT_TAKEN_TYPE])
        taken = SeatTaken()
        self.assertTrue(self.queue_publisher.published[0].envelope.payload.Unpack(taken))
        self.assertEqual(taken.table_id, EMPTY_TABLE_ID)
        self.assertEqual(taken.player_id, ONLOOKER)
        self.assertEqual(taken.seat_number, SECOND_SEAT)
        self.assertEqual(taken.version, result.table.version)
        self.assertTrue(taken.HasField("role"))

    async def test_standing_up_mid_game_publishes_the_withdrawal_before_the_seat(self) -> None:
        await self.start()
        self.queue_publisher.published.clear()

        await self.seats.vacate_seat(TABLE_ID, BLACK_PLAYER)

        self.assertEqual(
            [published.channel for published in self.queue_publisher.published],
            [SESSION_CHANNEL, TABLE_CHANNEL, LOBBY_CHANNEL],
        )
        self.assertEqual(
            self.queue_publisher.get_types_on(SESSION_CHANNEL), [PARTICIPANT_WITHDRAWN_TYPE]
        )
        self.assertEqual(self.queue_publisher.get_types_on(TABLE_CHANNEL), [SEAT_VACATED_TYPE])
        vacated = SeatVacated()
        self.assertTrue(self.queue_publisher.published[-1].envelope.payload.Unpack(vacated))
        self.assertEqual(vacated.seat_number, SECOND_SEAT)

    async def test_opening_joining_and_leaving_are_published(self) -> None:
        opened = await self.seats.create_table(GameType.GAME_TYPE_CHESS, CHESS_SEAT_COUNT, ONLOOKER)
        await self.seats.join_table(opened.table.id, WHITE_PLAYER)
        await self.seats.leave_table(opened.table.id, WHITE_PLAYER)

        self.assertEqual(
            self.queue_publisher.get_types_on(LOBBY_CHANNEL),
            [TABLE_CREATED_TYPE, PLAYER_JOINED_TYPE, PLAYER_LEFT_TYPE],
        )
        left = PlayerLeft()
        self.assertTrue(self.queue_publisher.published[-1].envelope.payload.Unpack(left))
        self.assertEqual(left.seat_number, NO_SEAT)

    async def test_a_refused_seat_change_publishes_nothing(self) -> None:
        await self.controller.take_seat(
            EMPTY_TABLE_ID,
            ONLOOKER,
            ChessSeatChoice(number=SECOND_SEAT, color=piece_pb2.COLOR_WHITE),
            FIRST_STORED_VERSION,
        )
        await self.seats.join_table(EMPTY_TABLE_ID, WHITE_PLAYER)
        await self.seats.vacate_seat(TABLE_ID, ONLOOKER)
        await self.seats.create_table(GameType.GAME_TYPE_CHESS, CHESS_SEAT_COUNT + 1, ONLOOKER)

        self.assertEqual(self.queue_publisher.published, [])
