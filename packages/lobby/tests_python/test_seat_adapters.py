import unittest

from idl.game.model.game_type_pb2 import GameType
from idl.lobby.model.seat_pb2 import Seat, SeatStatus
from idl.lobby.model.table_pb2 import Table, TableStatus

from lobby.adapters.seat_adapters import SeatAdapters

TABLE_ID = "t-1"
OPENER = "p-1"
JOINER = "p-2"
SEAT_COUNT = 3
STORED_VERSION = 4


class CreationToTableTest(unittest.TestCase):
    def test_the_opener_is_at_the_table_and_every_seat_is_open(self) -> None:
        table = SeatAdapters.creation_to_table(
            TABLE_ID, GameType.GAME_TYPE_CHESS, SEAT_COUNT, OPENER
        )
        self.assertEqual(table.id, TABLE_ID)
        self.assertEqual(table.game_type, GameType.GAME_TYPE_CHESS)
        self.assertEqual(table.status, TableStatus.TABLE_STATUS_WAITING)
        self.assertEqual(table.version, 0)
        self.assertEqual(list(table.player_ids), [OPENER])
        self.assertEqual([seat.number for seat in table.seats], [1, 2, 3])
        self.assertTrue(all(seat.status == SeatStatus.SEAT_STATUS_OPEN for seat in table.seats))


class TableWithPlayerJoinedTest(unittest.TestCase):
    def test_the_player_is_added_and_nothing_else_changes(self) -> None:
        before = Table(
            id=TABLE_ID,
            game_type=GameType.GAME_TYPE_CHESS,
            status=TableStatus.TABLE_STATUS_WAITING,
            seats=[Seat(number=1, status=SeatStatus.SEAT_STATUS_OCCUPIED, player_id=OPENER)],
            version=STORED_VERSION,
            player_ids=[OPENER],
        )
        after = SeatAdapters.table_to_table_with_player_joined(before, JOINER)
        self.assertEqual(list(after.player_ids), [OPENER, JOINER])
        self.assertEqual(after.seats, before.seats)
        self.assertEqual(after.version, STORED_VERSION)
        self.assertEqual(list(before.player_ids), [OPENER])
