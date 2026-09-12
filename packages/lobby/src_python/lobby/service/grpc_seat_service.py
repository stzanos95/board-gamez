"""
SeatService, as it is answered over gRPC.

Implements the servicer the schema generates. Every method is the same three
steps: adapt the request, call the controller, adapt what comes back. No field is
read off a request here, and nothing is decided.

The method names are the schema's, not this repository's. gRPC dispatches on
them, so they keep protobuf's casing; the per-file ignore in pyproject.toml is
what lets them.
"""

import grpc
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
from idl.lobby.service.seat_pb2_grpc import SeatServiceServicer

from lobby.adapters.seat_adapters import SeatAdapters
from lobby.controller.seat_controller import SeatController


class GrpcSeatService(SeatServiceServicer):
    """
    Every SeatService operation, as a gRPC call reaches it.
    """

    def __init__(self, controller: SeatController) -> None:
        self._controller = controller

    async def CreateTable(
        self,
        request: CreateTableRequest,
        context: grpc.aio.ServicerContext[CreateTableRequest, CreateTableResponse],
    ) -> CreateTableResponse:
        result = await self._controller.create_table(
            SeatAdapters.create_request_to_game_type(request),
            SeatAdapters.create_request_to_seat_count(request),
            SeatAdapters.create_request_to_player_id(request),
        )
        return SeatAdapters.seat_result_to_create_response(result)

    async def JoinTable(
        self,
        request: JoinTableRequest,
        context: grpc.aio.ServicerContext[JoinTableRequest, JoinTableResponse],
    ) -> JoinTableResponse:
        result = await self._controller.join_table(
            SeatAdapters.join_request_to_table_id(request),
            SeatAdapters.join_request_to_player_id(request),
        )
        return SeatAdapters.seat_result_to_join_response(result)

    async def VacateSeat(
        self,
        request: VacateSeatRequest,
        context: grpc.aio.ServicerContext[VacateSeatRequest, VacateSeatResponse],
    ) -> VacateSeatResponse:
        result = await self._controller.vacate_seat(
            SeatAdapters.vacate_request_to_table_id(request),
            SeatAdapters.vacate_request_to_player_id(request),
        )
        return SeatAdapters.seat_result_to_vacate_response(result)

    async def LeaveTable(
        self,
        request: LeaveTableRequest,
        context: grpc.aio.ServicerContext[LeaveTableRequest, LeaveTableResponse],
    ) -> LeaveTableResponse:
        result = await self._controller.leave_table(
            SeatAdapters.leave_request_to_table_id(request),
            SeatAdapters.leave_request_to_player_id(request),
        )
        return SeatAdapters.seat_result_to_leave_response(result)
