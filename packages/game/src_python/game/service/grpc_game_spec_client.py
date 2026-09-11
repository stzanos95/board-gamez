"""
GameSpecService, as it is called over gRPC.

The method names the stub dispatches on are the schema's, so they keep protobuf's
casing. Nothing outside this file sees them.
"""

from typing import cast

import grpc
from core.grpc.channel_options import ChannelOptions
from idl.game.dto.game_spec_pb2 import ListGameSpecRequest, ListGameSpecResponse
from idl.game.service.game_spec_pb2_grpc import GameSpecServiceAsyncStub, GameSpecServiceStub


class GrpcGameSpecClient:
    """
    Every GameSpecService operation, as a call leaves for the platform.

    Built unconnected; `connect` is called once the event loop is up, and
    `close` on the way down.
    """

    def __init__(self) -> None:
        self._channel: grpc.aio.Channel | None = None
        self._stub: GameSpecServiceAsyncStub | None = None

    async def connect(self, address: str, options: ChannelOptions) -> None:
        channel = grpc.aio.insecure_channel(address, options=options.to_options())
        self._channel = channel
        self._stub = cast(GameSpecServiceAsyncStub, GameSpecServiceStub(channel))

    async def close(self) -> None:
        if self._channel is not None:
            await self._channel.close()
            self._channel = None
            self._stub = None

    async def list_game_spec(self, request: ListGameSpecRequest) -> ListGameSpecResponse:
        return await self._connected_stub().ListGameSpec(request)

    def _connected_stub(self) -> GameSpecServiceAsyncStub:
        if self._stub is None:
            raise RuntimeError(
                "the game spec client was called before connect() opened its channel"
            )
        return self._stub
