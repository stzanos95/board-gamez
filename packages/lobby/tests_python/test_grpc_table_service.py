import unittest

from idl.lobby.dto.table_pb2 import (
    DeleteTableRequest,
    ListTableRequest,
    ReadTableRequest,
    UpsertTableRequest,
)
from idl.lobby.model.table_pb2 import Table

from lobby.controller.table_controller import TableController
from lobby.service.grpc_table_service import GrpcTableService

TABLE_ID = "t-1"
OTHER_TABLE_ID = "t-2"
EXPECTED_VERSION = 4


class RecordingController(TableController):
    """
    A controller that answers without deciding anything, so what the servicer
    unpacks is what the test can see.
    """

    def __init__(self) -> None:
        super().__init__()
        self.upserted: list[Table] = []
        self.read_ids: list[str] = []
        self.deleted: list[tuple[str, int]] = []
        self.stored: Table | None = None

    async def upsert_table(self, table: Table) -> Table:
        self.upserted.append(table)
        return table

    async def read_table(self, table_id: str) -> Table | None:
        self.read_ids.append(table_id)
        return self.stored

    async def delete_table(self, table_id: str, expected_version: int) -> None:
        self.deleted.append((table_id, expected_version))

    async def list_table(self) -> tuple[Table, ...]:
        return (Table(id=TABLE_ID), Table(id=OTHER_TABLE_ID))


class UnpackingTest(unittest.IsolatedAsyncioTestCase):
    """
    The servicer decides nothing. It hands the controller the arguments an
    operation takes, and packs what comes back into the schema's response.
    """

    async def test_an_upsert_reaches_the_controller_as_a_table(self) -> None:
        controller = RecordingController()
        service = GrpcTableService(controller=controller)
        table = Table(id=TABLE_ID)

        response = await service.UpsertTable(
            UpsertTableRequest(table=table),
            context=None,  # type: ignore[arg-type]
        )

        self.assertEqual(controller.upserted, [table])
        self.assertEqual(response.table.id, TABLE_ID)

    async def test_a_read_reaches_the_controller_as_an_id(self) -> None:
        controller = RecordingController()
        controller.stored = Table(id=TABLE_ID)
        service = GrpcTableService(controller=controller)

        response = await service.ReadTable(
            ReadTableRequest(table_id=TABLE_ID),
            context=None,  # type: ignore[arg-type]
        )

        self.assertEqual(controller.read_ids, [TABLE_ID])
        self.assertEqual(response.table.id, TABLE_ID)

    async def test_a_table_that_is_not_there_answers_with_an_unset_table(self) -> None:
        service = GrpcTableService(controller=RecordingController())

        response = await service.ReadTable(
            ReadTableRequest(table_id=TABLE_ID),
            context=None,  # type: ignore[arg-type]
        )

        self.assertFalse(response.HasField("table"))

    async def test_a_delete_carries_the_version_it_was_built_on(self) -> None:
        controller = RecordingController()
        service = GrpcTableService(controller=controller)

        response = await service.DeleteTable(
            DeleteTableRequest(table_id=TABLE_ID, expected_version=EXPECTED_VERSION),
            context=None,  # type: ignore[arg-type]
        )

        self.assertEqual(controller.deleted, [(TABLE_ID, EXPECTED_VERSION)])
        self.assertEqual(response.table_id, TABLE_ID)

    async def test_a_listing_is_packed_into_the_collection_the_schema_declares(self) -> None:
        service = GrpcTableService(controller=RecordingController())

        response = await service.ListTable(
            ListTableRequest(),
            context=None,  # type: ignore[arg-type]
        )

        self.assertEqual(
            [table.id for table in response.collection.table_items], [TABLE_ID, OTHER_TABLE_ID]
        )


class UnimplementedTest(unittest.IsolatedAsyncioTestCase):
    async def test_reading_is_not_written_yet(self) -> None:
        with self.assertRaises(NotImplementedError):
            await TableController().read_table(TABLE_ID)
