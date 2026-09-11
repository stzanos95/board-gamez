"""
GameSpecService, as it is answered over gRPC.

The method names are the schema's, not this repository's. gRPC dispatches on
them, so they keep protobuf's casing; the per-file ignore in pyproject.toml is
what lets them.
"""

import grpc
from idl.game.dto.game_spec_pb2 import ListGameSpecRequest, ListGameSpecResponse
from idl.game.service.game_spec_pb2_grpc import GameSpecServiceServicer

from game.adapters.game_spec_adapters import GameSpecAdapters
from game.controller.game_spec_controller import GameSpecController


class GrpcGameSpecService(GameSpecServiceServicer):
    """
    Every GameSpecService operation, as a gRPC call reaches it.
    """

    def __init__(self, controller: GameSpecController) -> None:
        self._controller = controller

    async def ListGameSpec(
        self,
        request: ListGameSpecRequest,
        context: grpc.aio.ServicerContext[ListGameSpecRequest, ListGameSpecResponse],
    ) -> ListGameSpecResponse:
        return GameSpecAdapters.game_spec_collection_to_list_response(
            await self._controller.list_game_spec()
        )
