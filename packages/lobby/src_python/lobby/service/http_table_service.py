"""
TableService, as it is answered over HTTP.

Implements the service the generated router declares, and answers each operation
by calling the lobby over gRPC. The service on the other end of that call is a
different implementation of the same four operations.

Converting between the two shapes of a message belongs to `lobby.adapters`, so
every method here is the same two steps: call, and hand back what came out.
"""

from idl_fastapi.idl.lobby.dto import (
    DeleteTableRequest,
    DeleteTableResponse,
    ListTableRequest,
    ListTableResponse,
    ReadTableRequest,
    ReadTableResponse,
    UpsertTableRequest,
    UpsertTableResponse,
)
from idl_fastapi.services.table_service import BaseTableService

from lobby.adapters.table_adapters import TableAdapters
from lobby.service.grpc_table_client import GrpcTableClient


class HttpTableService(BaseTableService):
    """
    Every TableService operation, as an HTTP request reaches it.
    """

    def __init__(self, client: GrpcTableClient) -> None:
        self._client = client

    async def upsert_table(self, request: UpsertTableRequest) -> UpsertTableResponse:
        response = await self._client.upsert_table(
            TableAdapters.upsert_request_model_to_message(request)
        )
        return TableAdapters.upsert_response_message_to_model(response)

    async def read_table(self, request: ReadTableRequest) -> ReadTableResponse:
        response = await self._client.read_table(
            TableAdapters.read_request_model_to_message(request)
        )
        return TableAdapters.read_response_message_to_model(response)

    async def delete_table(self, request: DeleteTableRequest) -> DeleteTableResponse:
        response = await self._client.delete_table(
            TableAdapters.delete_request_model_to_message(request)
        )
        return TableAdapters.delete_response_message_to_model(response)

    async def list_table(self, request: ListTableRequest) -> ListTableResponse:
        response = await self._client.list_table(
            TableAdapters.list_request_model_to_message(request)
        )
        return TableAdapters.list_response_message_to_model(response)
