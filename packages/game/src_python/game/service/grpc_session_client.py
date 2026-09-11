"""
SessionService, as it is called over gRPC.

The other half of what `GrpcSessionService` answers. A caller holds one of these
for the life of the process; the channel it dials is opened once at bringup and
closed when the process stops.

The method names the stub dispatches on are the schema's, so they keep protobuf's
casing. Nothing outside this file sees them.
"""

from typing import cast

import grpc
from core.grpc.channel_options import ChannelOptions
from idl.game.dto.command_pb2 import ApplyCommandRequest, ApplyCommandResponse
from idl.game.dto.session_pb2 import (
    CreateSessionRequest,
    CreateSessionResponse,
    ReadSessionRequest,
    ReadSessionResponse,
)
from idl.game.service.session_pb2_grpc import SessionServiceAsyncStub, SessionServiceStub


class GrpcSessionClient:
    """
    Every SessionService operation, as a call leaves for the platform.

    Built unconnected, because a gRPC channel belongs to a running event loop and
    there is none while an application is being assembled. `connect` is called
    once the loop is up, and `close` on the way down.
    """

    def __init__(self) -> None:
        self._channel: grpc.aio.Channel | None = None
        self._stub: SessionServiceAsyncStub | None = None

    async def connect(self, address: str, options: ChannelOptions) -> None:
        """
        Dial the platform. The channel connects lazily, so this does not block.
        """
        channel = grpc.aio.insecure_channel(address, options=options.to_options())
        self._channel = channel
        # One generated class constructs a stub for either channel type. The async
        # stub names the awaitable call types an aio channel answers with.
        self._stub = cast(SessionServiceAsyncStub, SessionServiceStub(channel))

    async def close(self) -> None:
        """
        Close the channel, letting calls already in flight finish.
        """
        if self._channel is not None:
            await self._channel.close()
            self._channel = None
            self._stub = None

    async def create_session(self, request: CreateSessionRequest) -> CreateSessionResponse:
        return await self._connected_stub().CreateSession(request)

    async def read_session(self, request: ReadSessionRequest) -> ReadSessionResponse:
        return await self._connected_stub().ReadSession(request)

    async def apply_command(self, request: ApplyCommandRequest) -> ApplyCommandResponse:
        return await self._connected_stub().ApplyCommand(request)

    def _connected_stub(self) -> SessionServiceAsyncStub:
        if self._stub is None:
            raise RuntimeError("the session client was called before connect() opened its channel")
        return self._stub
