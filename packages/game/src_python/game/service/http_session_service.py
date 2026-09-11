"""
SessionService, as it is answered over HTTP.

Implements the service the generated router declares, and answers each operation
by calling the platform over gRPC. The service on the other end of that call is
a different implementation of the same three operations.

Converting between the two shapes of a message belongs to `game.adapters`, so
every method here is the same two steps: call, and hand back what came out.
"""

from idl_fastapi.idl.game.dto import (
    ApplyCommandRequest,
    ApplyCommandResponse,
    CreateSessionRequest,
    CreateSessionResponse,
    ReadSessionRequest,
    ReadSessionResponse,
)
from idl_fastapi.services.session_service import BaseSessionService

from game.adapters.session_adapters import SessionAdapters
from game.service.grpc_session_client import GrpcSessionClient


class HttpSessionService(BaseSessionService):
    """
    Every SessionService operation, as an HTTP request reaches it.
    """

    def __init__(self, client: GrpcSessionClient) -> None:
        self._client = client

    async def create_session(self, request: CreateSessionRequest) -> CreateSessionResponse:
        response = await self._client.create_session(
            SessionAdapters.create_request_model_to_message(request)
        )
        return SessionAdapters.create_response_message_to_model(response)

    async def read_session(self, request: ReadSessionRequest) -> ReadSessionResponse:
        response = await self._client.read_session(
            SessionAdapters.read_request_model_to_message(request)
        )
        return SessionAdapters.read_response_message_to_model(response)

    async def apply_command(self, request: ApplyCommandRequest) -> ApplyCommandResponse:
        response = await self._client.apply_command(
            SessionAdapters.apply_request_model_to_message(request)
        )
        return SessionAdapters.apply_response_message_to_model(response)
