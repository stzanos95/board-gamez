"""
SessionService, as it is answered over gRPC.

Implements the servicer the schema generates. Every method is the same three
steps: adapt the request, call the controller, adapt what comes back. No field is
read off a request here, and nothing is decided.

The method names are the schema's, not this repository's. gRPC dispatches on
them, so they keep protobuf's casing; the per-file ignore in pyproject.toml is
what lets them.
"""

import grpc
from idl.game.dto.command_pb2 import ApplyCommandRequest, ApplyCommandResponse
from idl.game.dto.session_pb2 import (
    CreateSessionRequest,
    CreateSessionResponse,
    ReadSessionRequest,
    ReadSessionResponse,
    WithdrawPlayerRequest,
    WithdrawPlayerResponse,
)
from idl.game.service.session_pb2_grpc import SessionServiceServicer

from game.adapters.session_adapters import SessionAdapters
from game.controller.session_controller import SessionController


class GrpcSessionService(SessionServiceServicer):
    """
    Every SessionService operation, as a gRPC call reaches it.
    """

    def __init__(self, controller: SessionController) -> None:
        self._controller = controller

    async def CreateSession(
        self,
        request: CreateSessionRequest,
        context: grpc.aio.ServicerContext[CreateSessionRequest, CreateSessionResponse],
    ) -> CreateSessionResponse:
        session = await self._controller.create_session(
            SessionAdapters.create_request_to_table_id(request),
            SessionAdapters.create_request_to_game_type(request),
            SessionAdapters.create_request_to_participants(request),
            SessionAdapters.create_request_to_player_id(request),
        )
        return SessionAdapters.session_view_to_create_response(session)

    async def ReadSession(
        self,
        request: ReadSessionRequest,
        context: grpc.aio.ServicerContext[ReadSessionRequest, ReadSessionResponse],
    ) -> ReadSessionResponse:
        session = await self._controller.read_session(
            SessionAdapters.read_request_to_session_id(request),
            SessionAdapters.read_request_to_player_id(request),
        )
        return SessionAdapters.session_view_to_read_response(session)

    async def ApplyCommand(
        self,
        request: ApplyCommandRequest,
        context: grpc.aio.ServicerContext[ApplyCommandRequest, ApplyCommandResponse],
    ) -> ApplyCommandResponse:
        result = await self._controller.apply_command(
            SessionAdapters.apply_request_to_session_id(request),
            SessionAdapters.apply_request_to_player_id(request),
            SessionAdapters.apply_request_to_command_id(request),
            SessionAdapters.apply_request_to_action(request),
            SessionAdapters.apply_request_to_expected_version(request),
        )
        return SessionAdapters.command_result_to_apply_response(result)

    async def WithdrawPlayer(
        self,
        request: WithdrawPlayerRequest,
        context: grpc.aio.ServicerContext[WithdrawPlayerRequest, WithdrawPlayerResponse],
    ) -> WithdrawPlayerResponse:
        result = await self._controller.withdraw_player(
            SessionAdapters.withdraw_request_to_session_id(request),
            SessionAdapters.withdraw_request_to_player_id(request),
        )
        return SessionAdapters.withdrawal_result_to_withdraw_response(result)
