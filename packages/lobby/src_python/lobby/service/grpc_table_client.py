"""
TableService, as it is called over gRPC.

The other half of what `GrpcTableService` answers. A caller holds one of these
for the life of the process; the channel it dials is opened once at bringup and
closed when the process stops.

The method names the stub dispatches on are the schema's, so they keep protobuf's
casing. Nothing outside this file sees them.
"""

import grpc
from core.grpc.channel_options import ChannelOptions
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
from idl.lobby.service.table_pb2_grpc import TableServiceStub


class GrpcTableClient:
    """
    Every TableService operation, as a call leaves for the lobby.

    Built unconnected, because a gRPC channel belongs to a running event loop and
    there is none while an application is being assembled. `connect` is called
    once the loop is up, and `close` on the way down.
    """

    def __init__(self) -> None:
        self._channel: grpc.aio.Channel | None = None
        self._stub: TableServiceStub | None = None

    async def connect(self, address: str, options: ChannelOptions) -> None:
        """
        Dial the lobby. The channel connects lazily, so this does not block.
        """
        channel = grpc.aio.insecure_channel(address, options=options.to_options())
        self._channel = channel
        self._stub = TableServiceStub(channel)

    async def close(self) -> None:
        """
        Close the channel, letting calls already in flight finish.
        """
        if self._channel is not None:
            await self._channel.close()
            self._channel = None
            self._stub = None

    async def upsert_table(self, request: UpsertTableRequest) -> UpsertTableResponse:
        return await self._connected_stub().UpsertTable(request)

    async def read_table(self, request: ReadTableRequest) -> ReadTableResponse:
        return await self._connected_stub().ReadTable(request)

    async def delete_table(self, request: DeleteTableRequest) -> DeleteTableResponse:
        return await self._connected_stub().DeleteTable(request)

    async def list_table(self, request: ListTableRequest) -> ListTableResponse:
        return await self._connected_stub().ListTable(request)

    def _connected_stub(self) -> TableServiceStub:
        if self._stub is None:
            raise RuntimeError("the table client was called before connect() opened its channel")
        return self._stub
