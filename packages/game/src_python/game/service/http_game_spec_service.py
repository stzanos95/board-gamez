"""
GameSpecService, as it is answered over HTTP.
"""

from idl_fastapi.idl.game.dto import ListGameSpecRequest, ListGameSpecResponse
from idl_fastapi.services.game_spec_service import BaseGameSpecService

from game.adapters.game_spec_adapters import GameSpecAdapters
from game.service.grpc_game_spec_client import GrpcGameSpecClient


class HttpGameSpecService(BaseGameSpecService):
    """
    Every GameSpecService operation, as an HTTP request reaches it.
    """

    def __init__(self, client: GrpcGameSpecClient) -> None:
        self._client = client

    async def list_game_spec(self, request: ListGameSpecRequest) -> ListGameSpecResponse:
        response = await self._client.list_game_spec(
            GameSpecAdapters.list_request_model_to_message(request)
        )
        return GameSpecAdapters.list_response_message_to_model(response)
