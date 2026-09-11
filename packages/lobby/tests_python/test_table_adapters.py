import unittest

from idl.core.obj.object_metadata_pb2 import ObjectMetadata
from idl.game.model.game_type_pb2 import GameType
from idl.lobby.model.seat_pb2 import Seat, SeatStatus
from idl.lobby.model.table_pb2 import Table, TableStatus
from idl.lobby.obj.table_pb2 import TableObj

from lobby.adapters.table_adapters import TableAdapters

TABLE_ID = "t-1"
PLAYER_ID = "p-1"
WAITING_PLAYER_ID = "p-2"
STORED_VERSION = 3
CREATED_BY = "p-9"


class TableAdaptersTest(unittest.TestCase):
    """
    A table's own identity and version live in the stored table's metadata, and
    come back out of it unchanged.
    """

    def test_a_table_carries_its_id_and_version_into_the_metadata(self) -> None:
        stored = TableAdapters.table_to_table_obj(
            Table(
                id=TABLE_ID,
                game_type=GameType.GAME_TYPE_CHESS,
                status=TableStatus.TABLE_STATUS_WAITING,
                seats=[Seat(number=1, status=SeatStatus.SEAT_STATUS_OCCUPIED, player_id=PLAYER_ID)],
                version=STORED_VERSION,
                player_ids=[PLAYER_ID, WAITING_PLAYER_ID],
            )
        )

        self.assertEqual(stored.metadata.id, TABLE_ID)
        self.assertEqual(stored.metadata.version, STORED_VERSION)
        self.assertEqual(stored.game_type, GameType.GAME_TYPE_CHESS)
        self.assertEqual(stored.seats[0].player_id, PLAYER_ID)
        self.assertEqual(list(stored.player_ids), [PLAYER_ID, WAITING_PLAYER_ID])

    def test_a_stored_table_answers_as_the_table_it_holds(self) -> None:
        table = TableAdapters.table_obj_to_table(
            TableObj(
                metadata=ObjectMetadata(id=TABLE_ID, version=STORED_VERSION, created_by=CREATED_BY),
                game_type=GameType.GAME_TYPE_CHESS,
                status=TableStatus.TABLE_STATUS_IN_PROGRESS,
                seats=[Seat(number=1, status=SeatStatus.SEAT_STATUS_OPEN)],
                player_ids=[WAITING_PLAYER_ID],
            )
        )

        self.assertEqual(table.id, TABLE_ID)
        self.assertEqual(table.version, STORED_VERSION)
        self.assertEqual(table.status, TableStatus.TABLE_STATUS_IN_PROGRESS)
        self.assertEqual(list(table.player_ids), [WAITING_PLAYER_ID])

    def test_a_round_trip_leaves_the_table_unchanged(self) -> None:
        table = Table(
            id=TABLE_ID,
            game_type=GameType.GAME_TYPE_CHESS,
            status=TableStatus.TABLE_STATUS_WAITING,
            seats=[Seat(number=1, status=SeatStatus.SEAT_STATUS_OCCUPIED, player_id=PLAYER_ID)],
            version=STORED_VERSION,
            player_ids=[PLAYER_ID, WAITING_PLAYER_ID],
        )

        self.assertEqual(
            TableAdapters.table_obj_to_table(TableAdapters.table_to_table_obj(table)), table
        )
