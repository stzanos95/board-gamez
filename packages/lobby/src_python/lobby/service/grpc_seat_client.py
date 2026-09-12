"""
SeatService, as it is called over gRPC.

The other half of what `GrpcSeatService` answers. A caller holds one of these
for the life of the process; the channel it dials is opened once at bringup and
closed when the process stops.

The method names the stub dispatches on are the schema's, so they keep protobuf's
casing. Nothing outside this file sees them.
"""

from typing import cast

import grpc
from core.grpc.channel_options import ChannelOptions
from idl.lobby.dto.seat_pb2 import (
    CreateTableRequest,
    CreateTableResponse,
    JoinTableRequest,
    JoinTableResponse,
    LeaveTableRequest,
    LeaveTableResponse,
    VacateSeatRequest,
    VacateSeatResponse,
)
from idl.lobby.service.seat_pb2_grpc import SeatServiceAsyncStub, SeatServiceStub


class GrpcSeatClient:
    """
    Every SeatService operation, as a call leaves for the lobby.

    Built unconnected, because a gRPC channel belongs to a running event loop and
    there is none while an application is being assembled. `connect` is called
    once the loop is up, and `close` on the way down.
    """

    def __init__(self) -> None:
        self._channel: grpc.aio.Channel | None = None
        self._stub: SeatServiceAsyncStub | None = None

    async def connect(self, address: str, options: ChannelOptions) -> None:
        """
        Dial the lobby. The channel connects lazily, so this does not block.
        """
        channel = grpc.aio.insecure_channel(address, options=options.to_options())
        self._channel = channel
        # One generated class constructs a stub for either channel type. The async
        # stub names the awaitable call types an aio channel answers with.
        self._stub = cast(SeatServiceAsyncStub, SeatServiceStub(channel))

    async def close(self) -> None:
        """
        Close the channel, letting calls already in flight finish.
        """
        if self._channel is not None:
            await self._channel.close()
            self._channel = None
            self._stub = None

    async def create_table(self, request: CreateTableRequest) -> CreateTableResponse:
        return await self._connected_stub().CreateTable(request)

    async def join_table(self, request: JoinTableRequest) -> JoinTableResponse:
        return await self._connected_stub().JoinTable(request)

    async def vacate_seat(self, request: VacateSeatRequest) -> VacateSeatResponse:
        return await self._connected_stub().VacateSeat(request)

    async def leave_table(self, request: LeaveTableRequest) -> LeaveTableResponse:
        return await self._connected_stub().LeaveTable(request)

    def _connected_stub(self) -> SeatServiceAsyncStub:
        if self._stub is None:
            raise RuntimeError("the seat client was called before connect() opened its channel")
        return self._stub
