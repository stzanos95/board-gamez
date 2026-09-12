"""
UnoService, as it is answered over gRPC.

Implements the servicer the schema generates. Every method is the same three
steps: adapt the request, call the controller, adapt what comes back. No field is
read off a request here, and nothing is decided.

The method names are the schema's, not this repository's. gRPC dispatches on
them, so they keep protobuf's casing; the per-file ignore in pyproject.toml is
what lets them.
"""

import grpc
from idl.uno.dto.game_pb2 import (
    PlayActionRequest,
    PlayActionResponse,
    ReadGameRequest,
    ReadGameResponse,
    StartGameRequest,
    StartGameResponse,
)
from idl.uno.dto.table_pb2 import (
    ListSeatChoiceRequest,
    ListSeatChoiceResponse,
    ReadTableRequest,
    ReadTableResponse,
    TakeSeatRequest,
    TakeSeatResponse,
)
from idl.uno.service.game_pb2_grpc import UnoServiceServicer

from product_uno.adapters.uno_seat_adapters import UnoSeatAdapters
from product_uno.adapters.uno_session_adapters import UnoSessionAdapters
from product_uno.controller.uno_session_controller import UnoSessionController


class GrpcUnoService(UnoServiceServicer):
    """
    Every UnoService operation, as a gRPC call reaches it.
    """

    def __init__(self, controller: UnoSessionController) -> None:
        self._controller = controller

    async def ReadTable(
        self,
        request: ReadTableRequest,
        context: grpc.aio.ServicerContext[ReadTableRequest, ReadTableResponse],
    ) -> ReadTableResponse:
        table = await self._controller.read_table(
            UnoSeatAdapters.read_table_request_to_table_id(request)
        )
        return UnoSeatAdapters.uno_table_to_read_response(table)

    async def ListSeatChoice(
        self,
        request: ListSeatChoiceRequest,
        context: grpc.aio.ServicerContext[ListSeatChoiceRequest, ListSeatChoiceResponse],
    ) -> ListSeatChoiceResponse:
        collection = await self._controller.list_seat_choices(
            UnoSeatAdapters.list_request_to_table_id(request),
            UnoSeatAdapters.list_request_to_player_id(request),
        )
        return UnoSeatAdapters.uno_seat_choice_collection_to_list_response(collection)

    async def TakeSeat(
        self,
        request: TakeSeatRequest,
        context: grpc.aio.ServicerContext[TakeSeatRequest, TakeSeatResponse],
    ) -> TakeSeatResponse:
        result = await self._controller.take_seat(
            UnoSeatAdapters.take_request_to_table_id(request),
            UnoSeatAdapters.take_request_to_player_id(request),
            UnoSeatAdapters.take_request_to_choice(request),
            UnoSeatAdapters.take_request_to_expected_version(request),
        )
        return UnoSeatAdapters.uno_seat_result_to_take_response(result)

    async def StartGame(
        self,
        request: StartGameRequest,
        context: grpc.aio.ServicerContext[StartGameRequest, StartGameResponse],
    ) -> StartGameResponse:
        session = await self._controller.start_game(
            UnoSessionAdapters.start_request_to_table_id(request),
            UnoSessionAdapters.start_request_to_player_id(request),
        )
        return UnoSessionAdapters.uno_session_to_start_response(session)

    async def ReadGame(
        self,
        request: ReadGameRequest,
        context: grpc.aio.ServicerContext[ReadGameRequest, ReadGameResponse],
    ) -> ReadGameResponse:
        session = await self._controller.read_game(
            UnoSessionAdapters.read_request_to_table_id(request),
            UnoSessionAdapters.read_request_to_player_id(request),
        )
        return UnoSessionAdapters.uno_session_to_read_response(session)

    async def PlayAction(
        self,
        request: PlayActionRequest,
        context: grpc.aio.ServicerContext[PlayActionRequest, PlayActionResponse],
    ) -> PlayActionResponse:
        result = await self._controller.play_action(
            UnoSessionAdapters.play_request_to_table_id(request),
            UnoSessionAdapters.play_request_to_player_id(request),
            UnoSessionAdapters.play_request_to_command_id(request),
            UnoSessionAdapters.play_request_to_action(request),
            UnoSessionAdapters.play_request_to_expected_version(request),
        )
        return UnoSessionAdapters.action_result_to_play_response(result)
