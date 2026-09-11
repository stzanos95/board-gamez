"""
ChessService, as it is called over gRPC.

The other half of what `GrpcChessService` answers. A caller holds one of these
for the life of the process; the channel it dials is opened once at bringup and
closed when the process stops.

The method names the stub dispatches on are the schema's, so they keep protobuf's
casing. Nothing outside this file sees them.
"""

from typing import cast

import grpc
from core.grpc.channel_options import ChannelOptions
from idl.chess.dto.game_pb2 import (
    PlayActionRequest,
    PlayActionResponse,
    ReadGameRequest,
    ReadGameResponse,
    StartGameRequest,
    StartGameResponse,
)
from idl.chess.service.game_pb2_grpc import ChessServiceAsyncStub, ChessServiceStub


class GrpcChessClient:
    """
    Every ChessService operation, as a call leaves for the platform.

    Built unconnected, because a gRPC channel belongs to a running event loop and
    there is none while an application is being assembled. `connect` is called
    once the loop is up, and `close` on the way down.
    """

    def __init__(self) -> None:
        self._channel: grpc.aio.Channel | None = None
        self._stub: ChessServiceAsyncStub | None = None

    async def connect(self, address: str, options: ChannelOptions) -> None:
        """
        Dial the platform. The channel connects lazily, so this does not block.
        """
        channel = grpc.aio.insecure_channel(address, options=options.to_options())
        self._channel = channel
        # One generated class constructs a stub for either channel type. The async
        # stub names the awaitable call types an aio channel answers with.
        self._stub = cast(ChessServiceAsyncStub, ChessServiceStub(channel))

    async def close(self) -> None:
        """
        Close the channel, letting calls already in flight finish.
        """
        if self._channel is not None:
            await self._channel.close()
            self._channel = None
            self._stub = None

    async def start_game(self, request: StartGameRequest) -> StartGameResponse:
        return await self._connected_stub().StartGame(request)

    async def read_game(self, request: ReadGameRequest) -> ReadGameResponse:
        return await self._connected_stub().ReadGame(request)

    async def play_action(self, request: PlayActionRequest) -> PlayActionResponse:
        return await self._connected_stub().PlayAction(request)

    def _connected_stub(self) -> ChessServiceAsyncStub:
        if self._stub is None:
            raise RuntimeError("the chess client was called before connect() opened its channel")
        return self._stub
