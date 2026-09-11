"""
GameSpecService, generated from the OpenAPI document. Do not edit.

BaseGameSpecService declares one method per operation, and
GameSpecServiceRouter.build binds every path to an instance of it. The
implementation belongs to the domain package that owns this service.
"""

from abc import ABC, abstractmethod

from fastapi import APIRouter

from idl_fastapi.google.rpc import Status
from idl_fastapi.idl.game.dto import ListGameSpecRequest, ListGameSpecResponse


SERVICE_TAG = "GameSpecService"


class BaseGameSpecService(ABC):
    """
    What an implementation of GameSpecService must answer.
    """

    @abstractmethod
    async def list_game_spec(
        self,
        request: ListGameSpecRequest,
    ) -> ListGameSpecResponse:
        """
        POST /internal/platform/game/list/game_spec
        """


class GameSpecServiceRouter:
    """
    The paths GameSpecService declares, bound to an implementation.
    """

    @staticmethod
    def build(service: BaseGameSpecService) -> APIRouter:
        """
        A router answering every GameSpecService path through `service`.
        """
        router = APIRouter(tags=[SERVICE_TAG])

        @router.post(
            "/internal/platform/game/list/game_spec",
            operation_id="GameSpecService_ListGameSpec",
            response_model=ListGameSpecResponse,
            response_model_exclude_none=True,
            responses={"default": {"model": Status}},
        )
        async def list_game_spec(
            request: ListGameSpecRequest,
        ) -> ListGameSpecResponse:
            return await service.list_game_spec(
                request=request,
            )

        return router
