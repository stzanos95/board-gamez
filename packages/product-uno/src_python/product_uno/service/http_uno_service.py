"""
UnoService, as it is answered over HTTP.

Implements the service the generated router declares, and answers each operation
by calling the platform over gRPC. The service on the other end of that call is
a different implementation of the same operations.

Converting between the two shapes of a message belongs to
`product_uno.adapters`, so every method here is the same two steps: call, and
hand back what came out.
"""

from idl_fastapi.idl.uno.dto import (
    ListSeatChoiceRequest,
    ListSeatChoiceResponse,
    PlayActionRequest,
    PlayActionResponse,
    ReadGameRequest,
    ReadGameResponse,
    ReadTableRequest,
    ReadTableResponse,
    StartGameRequest,
    StartGameResponse,
    TakeSeatRequest,
    TakeSeatResponse,
)
from idl_fastapi.services.uno_service import BaseUnoService

from product_uno.adapters.uno_seat_adapters import UnoSeatAdapters
from product_uno.adapters.uno_session_adapters import UnoSessionAdapters
from product_uno.service.grpc_uno_client import GrpcUnoClient


class HttpUnoService(BaseUnoService):
    """
    Every UnoService operation, as an HTTP request reaches it.
    """

    def __init__(self, client: GrpcUnoClient) -> None:
        self._client = client

    async def read_table(self, request: ReadTableRequest) -> ReadTableResponse:
        response = await self._client.read_table(
            UnoSeatAdapters.read_table_request_model_to_message(request)
        )
        return UnoSeatAdapters.read_table_response_message_to_model(response)

    async def list_seat_choice(self, request: ListSeatChoiceRequest) -> ListSeatChoiceResponse:
        response = await self._client.list_seat_choice(
            UnoSeatAdapters.list_request_model_to_message(request)
        )
        return UnoSeatAdapters.list_response_message_to_model(response)

    async def take_seat(self, request: TakeSeatRequest) -> TakeSeatResponse:
        response = await self._client.take_seat(
            UnoSeatAdapters.take_request_model_to_message(request)
        )
        return UnoSeatAdapters.take_response_message_to_model(response)

    async def start_game(self, request: StartGameRequest) -> StartGameResponse:
        response = await self._client.start_game(
            UnoSessionAdapters.start_request_model_to_message(request)
        )
        return UnoSessionAdapters.start_response_message_to_model(response)

    async def read_game(self, request: ReadGameRequest) -> ReadGameResponse:
        response = await self._client.read_game(
            UnoSessionAdapters.read_request_model_to_message(request)
        )
        return UnoSessionAdapters.read_response_message_to_model(response)

    async def play_action(self, request: PlayActionRequest) -> PlayActionResponse:
        response = await self._client.play_action(
            UnoSessionAdapters.play_request_model_to_message(request)
        )
        return UnoSessionAdapters.play_response_message_to_model(response)
