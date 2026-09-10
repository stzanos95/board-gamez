"""
TableService, as it is answered over gRPC.

Implements the servicer the schema generates. Every method is the same three
steps: adapt the request, call the controller, adapt what comes back. No field is
read off a request here, and nothing is decided.

The method names are the schema's, not this repository's. gRPC dispatches on
them, so they keep protobuf's casing; the per-file ignore in pyproject.toml is
what lets them.
"""

import grpc
from idl.lobby.dto.table_pb2 import (
    DeleteTableRequest,
    DeleteTableResponse,
    ListTableRequest,
    ListTableResponse,
    ReadTableRequest,
    ReadTableResponse,
    UpsertTableRequest,
    UpsertTableResponse,
)
from idl.lobby.service.table_pb2_grpc import TableServiceServicer

from lobby.adapters.table_adapters import TableAdapters
from lobby.controller.table_controller import TableController


class GrpcTableService(TableServiceServicer):
    """
    Every TableService operation, as a gRPC call reaches it.
    """

    def __init__(self, controller: TableController) -> None:
        self._controller = controller

    async def UpsertTable(
        self,
        request: UpsertTableRequest,
        context: grpc.aio.ServicerContext[UpsertTableRequest, UpsertTableResponse],
    ) -> UpsertTableResponse:
        table = await self._controller.upsert_table(TableAdapters.upsert_request_to_table(request))
        return TableAdapters.table_to_upsert_response(table)

    async def ReadTable(
        self,
        request: ReadTableRequest,
        context: grpc.aio.ServicerContext[ReadTableRequest, ReadTableResponse],
    ) -> ReadTableResponse:
        table = await self._controller.read_table(TableAdapters.read_request_to_table_id(request))
        return TableAdapters.table_to_read_response(table)

    async def DeleteTable(
        self,
        request: DeleteTableRequest,
        context: grpc.aio.ServicerContext[DeleteTableRequest, DeleteTableResponse],
    ) -> DeleteTableResponse:
        table_id = TableAdapters.delete_request_to_table_id(request)
        await self._controller.delete_table(
            table_id, TableAdapters.delete_request_to_expected_version(request)
        )
        return TableAdapters.table_id_to_delete_response(table_id)

    async def ListTable(
        self,
        request: ListTableRequest,
        context: grpc.aio.ServicerContext[ListTableRequest, ListTableResponse],
    ) -> ListTableResponse:
        return TableAdapters.table_collection_to_list_response(await self._controller.list_table())
