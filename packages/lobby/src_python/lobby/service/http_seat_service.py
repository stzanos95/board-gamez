"""
SeatService, as it is answered over HTTP.

Implements the service the generated router declares, and answers each operation
by calling the lobby over gRPC. The service on the other end of that call is a
different implementation of the same two operations.

Converting between the two shapes of a message belongs to `lobby.adapters`, so
every method here is the same two steps: call, and hand back what came out.
"""

from idl_fastapi.idl.lobby.dto import (
    LeaveTableRequest,
    LeaveTableResponse,
    VacateSeatRequest,
    VacateSeatResponse,
)
from idl_fastapi.services.seat_service import BaseSeatService

from lobby.adapters.seat_adapters import SeatAdapters
from lobby.service.grpc_seat_client import GrpcSeatClient


class HttpSeatService(BaseSeatService):
    """
    Every SeatService operation, as an HTTP request reaches it.
    """

    def __init__(self, client: GrpcSeatClient) -> None:
        self._client = client

    async def vacate_seat(self, request: VacateSeatRequest) -> VacateSeatResponse:
        response = await self._client.vacate_seat(
            SeatAdapters.vacate_request_model_to_message(request)
        )
        return SeatAdapters.vacate_response_message_to_model(response)

    async def leave_table(self, request: LeaveTableRequest) -> LeaveTableResponse:
        response = await self._client.leave_table(
            SeatAdapters.leave_request_model_to_message(request)
        )
        return SeatAdapters.leave_response_message_to_model(response)
