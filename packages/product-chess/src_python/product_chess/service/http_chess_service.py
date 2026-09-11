"""
ChessService, as it is answered over HTTP.

Implements the service the generated router declares, and answers each operation
by calling the platform over gRPC. The service on the other end of that call is
a different implementation of the same three operations.

Converting between the two shapes of a message belongs to
`product_chess.adapters`, so every method here is the same two steps: call, and
hand back what came out.
"""

from idl_fastapi.idl.chess.dto import (
    PlayActionRequest,
    PlayActionResponse,
    ReadGameRequest,
    ReadGameResponse,
    StartGameRequest,
    StartGameResponse,
)
from idl_fastapi.services.chess_service import BaseChessService

from product_chess.adapters.chess_session_adapters import ChessSessionAdapters
from product_chess.service.grpc_chess_client import GrpcChessClient


class HttpChessService(BaseChessService):
    """
    Every ChessService operation, as an HTTP request reaches it.
    """

    def __init__(self, client: GrpcChessClient) -> None:
        self._client = client

    async def start_game(self, request: StartGameRequest) -> StartGameResponse:
        response = await self._client.start_game(
            ChessSessionAdapters.start_request_model_to_message(request)
        )
        return ChessSessionAdapters.start_response_message_to_model(response)

    async def read_game(self, request: ReadGameRequest) -> ReadGameResponse:
        response = await self._client.read_game(
            ChessSessionAdapters.read_request_model_to_message(request)
        )
        return ChessSessionAdapters.read_response_message_to_model(response)

    async def play_action(self, request: PlayActionRequest) -> PlayActionResponse:
        response = await self._client.play_action(
            ChessSessionAdapters.play_request_model_to_message(request)
        )
        return ChessSessionAdapters.play_response_message_to_model(response)
