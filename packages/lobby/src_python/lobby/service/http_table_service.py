"""
TableService, as it is answered over HTTP.

Implements the service the generated router declares, and answers each operation
by calling the lobby over gRPC. The service on the other end of that call is a
different implementation of the same four operations.

Each method is where the call goes, and none of them is written yet.
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


class HttpTableService(BaseTableService):
    """
    Every TableService operation, as an HTTP request reaches it.
    """

    async def upsert_table(self, request: UpsertTableRequest) -> UpsertTableResponse:
        raise NotImplementedError

    async def read_table(self, request: ReadTableRequest) -> ReadTableResponse:
        raise NotImplementedError

    async def delete_table(self, request: DeleteTableRequest) -> DeleteTableResponse:
        raise NotImplementedError

    async def list_table(self, request: ListTableRequest) -> ListTableResponse:
        raise NotImplementedError
