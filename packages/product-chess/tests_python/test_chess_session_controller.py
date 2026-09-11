import unittest

from game.controller.rules_registry import RulesRegistry
from game.controller.session_controller import SessionController
from idl.chess.model import piece_pb2
from idl.chess.model.session_pb2 import ChessSession
from idl.game.model.command_result_pb2 import CommandOutcome
from idl.game.model.game_type_pb2 import GameType
from idl.lobby.model.seat_pb2 import Seat, SeatStatus
from idl.lobby.model.table_pb2 import Table, TableStatus
from lobby.controller.table_controller import TableController

from product_chess.controller.chess_rules import ChessRules
from product_chess.controller.chess_session_controller import ChessSessionController
from tests_python.chess_actions import move, resignation
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
COMMAND_ID = "c-1"
OTHER_COMMAND_ID = "c-2"


def occupied(number: int, player_id: str) -> Seat:
    return Seat(number=number, status=SeatStatus.SEAT_STATUS_OCCUPIED, player_id=player_id)


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
        self.tables = TableController(repository=InMemoryTableRepository())
        self.sessions = SessionController(
            repository=InMemorySessionRepository(),
            rules=RulesRegistry({GameType.GAME_TYPE_CHESS: ChessRules()}),
        )
        self.controller = ChessSessionController(tables=self.tables, sessions=self.sessions)
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

    async def start(self, player_id: str = WHITE_PLAYER) -> ChessSession:
        return require_session(await self.controller.start_game(TABLE_ID, player_id))

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
