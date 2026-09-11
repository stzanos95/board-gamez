"""
ChessService, as it is answered over gRPC.

Implements the servicer the schema generates. Every method is the same three
steps: adapt the request, call the controller, adapt what comes back. No field is
read off a request here, and nothing is decided.

The method names are the schema's, not this repository's. gRPC dispatches on
them, so they keep protobuf's casing; the per-file ignore in pyproject.toml is
what lets them.
"""

import grpc
from idl.chess.dto.game_pb2 import (
    PlayActionRequest,
    PlayActionResponse,
    ReadGameRequest,
    ReadGameResponse,
    StartGameRequest,
    StartGameResponse,
)
from idl.chess.service.game_pb2_grpc import ChessServiceServicer

from product_chess.adapters.chess_session_adapters import ChessSessionAdapters
from product_chess.controller.chess_session_controller import ChessSessionController


class GrpcChessService(ChessServiceServicer):
    """
    Every ChessService operation, as a gRPC call reaches it.
    """

    def __init__(self, controller: ChessSessionController) -> None:
        self._controller = controller

    async def StartGame(
        self,
        request: StartGameRequest,
        context: grpc.aio.ServicerContext[StartGameRequest, StartGameResponse],
    ) -> StartGameResponse:
        session = await self._controller.start_game(
            ChessSessionAdapters.start_request_to_table_id(request),
            ChessSessionAdapters.start_request_to_player_id(request),
        )
        return ChessSessionAdapters.chess_session_to_start_response(session)

    async def ReadGame(
        self,
        request: ReadGameRequest,
        context: grpc.aio.ServicerContext[ReadGameRequest, ReadGameResponse],
    ) -> ReadGameResponse:
        session = await self._controller.read_game(
            ChessSessionAdapters.read_request_to_table_id(request),
            ChessSessionAdapters.read_request_to_player_id(request),
        )
        return ChessSessionAdapters.chess_session_to_read_response(session)

    async def PlayAction(
        self,
        request: PlayActionRequest,
        context: grpc.aio.ServicerContext[PlayActionRequest, PlayActionResponse],
    ) -> PlayActionResponse:
        result = await self._controller.play_action(
            ChessSessionAdapters.play_request_to_table_id(request),
            ChessSessionAdapters.play_request_to_player_id(request),
            ChessSessionAdapters.play_request_to_command_id(request),
            ChessSessionAdapters.play_request_to_action(request),
            ChessSessionAdapters.play_request_to_expected_version(request),
        )
        return ChessSessionAdapters.action_result_to_play_response(result)
