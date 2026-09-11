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
from idl.chess.dto.table_pb2 import (
    ListSeatChoiceRequest,
    ListSeatChoiceResponse,
    ReadTableRequest,
    ReadTableResponse,
    TakeSeatRequest,
    TakeSeatResponse,
)
from idl.chess.service.game_pb2_grpc import ChessServiceServicer

from product_chess.adapters.chess_seat_adapters import ChessSeatAdapters
from product_chess.adapters.chess_session_adapters import ChessSessionAdapters
from product_chess.controller.chess_session_controller import ChessSessionController


class GrpcChessService(ChessServiceServicer):
    """
    Every ChessService operation, as a gRPC call reaches it.
    """

    def __init__(self, controller: ChessSessionController) -> None:
        self._controller = controller

    async def ReadTable(
        self,
        request: ReadTableRequest,
        context: grpc.aio.ServicerContext[ReadTableRequest, ReadTableResponse],
    ) -> ReadTableResponse:
        table = await self._controller.read_table(
            ChessSeatAdapters.read_table_request_to_table_id(request)
        )
        return ChessSeatAdapters.chess_table_to_read_response(table)

    async def ListSeatChoice(
        self,
        request: ListSeatChoiceRequest,
        context: grpc.aio.ServicerContext[ListSeatChoiceRequest, ListSeatChoiceResponse],
    ) -> ListSeatChoiceResponse:
        collection = await self._controller.list_seat_choices(
            ChessSeatAdapters.list_request_to_table_id(request),
            ChessSeatAdapters.list_request_to_player_id(request),
        )
        return ChessSeatAdapters.chess_seat_choice_collection_to_list_response(collection)

    async def TakeSeat(
        self,
        request: TakeSeatRequest,
        context: grpc.aio.ServicerContext[TakeSeatRequest, TakeSeatResponse],
    ) -> TakeSeatResponse:
        result = await self._controller.take_seat(
            ChessSeatAdapters.take_request_to_table_id(request),
            ChessSeatAdapters.take_request_to_player_id(request),
            ChessSeatAdapters.take_request_to_choice(request),
            ChessSeatAdapters.take_request_to_expected_version(request),
        )
        return ChessSeatAdapters.chess_seat_result_to_take_response(result)

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
