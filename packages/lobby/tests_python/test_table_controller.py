import unittest

from idl.game.model.game_type_pb2 import GameType
from idl.lobby.model.event_pb2 import TableClosed
from idl.lobby.model.seat_pb2 import Seat, SeatStatus
from idl.lobby.model.table_pb2 import Table, TableStatus

from lobby.controller.table_controller import TableController
from tests_python.in_memory_queue_publisher import InMemoryQueuePublisher
from tests_python.in_memory_table_repository import InMemoryTableRepository

TABLE_ID = "t-1"
OTHER_TABLE_ID = "t-2"
PLAYER_ID = "p-1"
UNSTORED_VERSION = 0
FIRST_STORED_VERSION = 1
SECOND_STORED_VERSION = 2
STALE_VERSION = 7
MISSING_TABLE_ID = "t-9"
TABLE_CHANNEL = "table:t-1"
LOBBY_CHANNEL = "lobby"
TABLE_CLOSED_TYPE = "idl.lobby.model.TableClosed"


class TableControllerTest(unittest.IsolatedAsyncioTestCase):
    """
    What a table operation means, against a store that keeps its tables in a
    dictionary.
    """

    def setUp(self) -> None:
        self.queue_publisher = InMemoryQueuePublisher()
        self.controller = TableController(
            repository=InMemoryTableRepository(), queue_publisher=self.queue_publisher
        )

    async def upsert(self, table: Table) -> Table:
        """
        A write the test expects to be accepted.
        """
        stored = await self.controller.upsert_table(table)
        assert stored is not None
        return stored

    async def test_a_table_that_was_never_stored_is_created_at_the_first_version(self) -> None:
        stored = await self.upsert(
            Table(
                id=TABLE_ID,
                game_type=GameType.GAME_TYPE_CHESS,
                status=TableStatus.TABLE_STATUS_WAITING,
                seats=[Seat(number=1, status=SeatStatus.SEAT_STATUS_OPEN)],
                version=UNSTORED_VERSION,
            )
        )

        self.assertEqual(stored.id, TABLE_ID)
        self.assertEqual(stored.version, FIRST_STORED_VERSION)
        self.assertEqual(stored.game_type, GameType.GAME_TYPE_CHESS)
        self.assertEqual(len(stored.seats), 1)

    async def test_a_write_at_the_stored_version_moves_the_table_on(self) -> None:
        created = await self.upsert(Table(id=TABLE_ID, version=UNSTORED_VERSION))

        seated = Table(
            id=TABLE_ID,
            seats=[Seat(number=1, status=SeatStatus.SEAT_STATUS_OCCUPIED, player_id=PLAYER_ID)],
            version=created.version,
        )
        stored = await self.upsert(seated)

        self.assertEqual(stored.version, SECOND_STORED_VERSION)
        self.assertEqual(stored.seats[0].player_id, PLAYER_ID)

    async def test_a_write_built_on_an_earlier_version_writes_nothing(self) -> None:
        created = await self.upsert(Table(id=TABLE_ID, version=UNSTORED_VERSION))

        refused = await self.controller.upsert_table(Table(id=TABLE_ID, version=UNSTORED_VERSION))

        self.assertIsNone(refused)
        stored = await self.controller.read_table(TABLE_ID)
        assert stored is not None
        self.assertEqual(stored.version, created.version)

    async def test_reading_an_id_nothing_is_stored_under_answers_nothing(self) -> None:
        self.assertIsNone(await self.controller.read_table(TABLE_ID))

    async def test_a_stored_table_reads_back_as_it_was_written(self) -> None:
        await self.upsert(
            Table(
                id=TABLE_ID,
                game_type=GameType.GAME_TYPE_CHESS,
                status=TableStatus.TABLE_STATUS_IN_PROGRESS,
                version=UNSTORED_VERSION,
            )
        )

        table = await self.controller.read_table(TABLE_ID)

        self.assertIsNotNone(table)
        assert table is not None
        self.assertEqual(table.status, TableStatus.TABLE_STATUS_IN_PROGRESS)
        self.assertEqual(table.version, FIRST_STORED_VERSION)

    async def test_a_delete_at_the_stored_version_removes_the_table(self) -> None:
        created = await self.upsert(Table(id=TABLE_ID, version=UNSTORED_VERSION))

        await self.controller.delete_table(TABLE_ID, created.version)

        self.assertIsNone(await self.controller.read_table(TABLE_ID))

    async def test_a_delete_at_another_version_leaves_the_table_alone(self) -> None:
        await self.upsert(Table(id=TABLE_ID, version=UNSTORED_VERSION))

        await self.controller.delete_table(TABLE_ID, STALE_VERSION)

        self.assertIsNotNone(await self.controller.read_table(TABLE_ID))

    async def test_a_listing_answers_every_stored_table(self) -> None:
        await self.upsert(Table(id=TABLE_ID, version=UNSTORED_VERSION))
        await self.upsert(Table(id=OTHER_TABLE_ID, version=UNSTORED_VERSION))

        collection = await self.controller.list_table()

        self.assertEqual(
            sorted(table.id for table in collection.table_items), [TABLE_ID, OTHER_TABLE_ID]
        )

    # --- publishing ----------------------------------------------------------

    async def test_a_delete_that_removes_the_table_is_published_as_closed(self) -> None:
        created = await self.upsert(Table(id=TABLE_ID, version=UNSTORED_VERSION))

        await self.controller.delete_table(TABLE_ID, created.version)

        self.assertEqual(self.queue_publisher.get_types_on(TABLE_CHANNEL), [TABLE_CLOSED_TYPE])
        self.assertEqual(self.queue_publisher.get_types_on(LOBBY_CHANNEL), [TABLE_CLOSED_TYPE])
        closed = TableClosed()
        self.assertTrue(self.queue_publisher.published[0].envelope.payload.Unpack(closed))
        self.assertEqual(closed.table_id, TABLE_ID)

    async def test_a_delete_that_removes_nothing_publishes_nothing(self) -> None:
        await self.upsert(Table(id=TABLE_ID, version=UNSTORED_VERSION))

        await self.controller.delete_table(TABLE_ID, STALE_VERSION)
        await self.controller.delete_table(MISSING_TABLE_ID, FIRST_STORED_VERSION)

        self.assertEqual(self.queue_publisher.published, [])

    async def test_an_upsert_through_the_store_publishes_nothing(self) -> None:
        await self.upsert(Table(id=TABLE_ID, version=UNSTORED_VERSION))

        self.assertEqual(self.queue_publisher.published, [])
