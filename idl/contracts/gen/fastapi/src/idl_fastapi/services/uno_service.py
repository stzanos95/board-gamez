"""
UnoService, generated from the OpenAPI document. Do not edit.

BaseUnoService declares one method per operation, and
UnoServiceRouter.build binds every path to an instance of it. The
implementation belongs to the domain package that owns this service.
"""

from abc import ABC, abstractmethod

from fastapi import APIRouter

from idl_fastapi.google.rpc import Status
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


SERVICE_TAG = "UnoService"


class BaseUnoService(ABC):
    """
    What an implementation of UnoService must answer.
    """

    @abstractmethod
    async def list_seat_choice(
        self,
        request: ListSeatChoiceRequest,
    ) -> ListSeatChoiceResponse:
        """
        POST /internal/product/uno/list/seat_choice
        """

    @abstractmethod
    async def play_action(
        self,
        request: PlayActionRequest,
    ) -> PlayActionResponse:
        """
        POST /internal/product/uno/play/action
        """

    @abstractmethod
    async def read_game(
        self,
        request: ReadGameRequest,
    ) -> ReadGameResponse:
        """
        POST /internal/product/uno/read/game
        """

    @abstractmethod
    async def read_table(
        self,
        request: ReadTableRequest,
    ) -> ReadTableResponse:
        """
        POST /internal/product/uno/read/table
        """

    @abstractmethod
    async def start_game(
        self,
        request: StartGameRequest,
    ) -> StartGameResponse:
        """
        POST /internal/product/uno/start/game
        """

    @abstractmethod
    async def take_seat(
        self,
        request: TakeSeatRequest,
    ) -> TakeSeatResponse:
        """
        POST /internal/product/uno/take/seat
        """


class UnoServiceRouter:
    """
    The paths UnoService declares, bound to an implementation.
    """

    @staticmethod
    def build(service: BaseUnoService) -> APIRouter:
        """
        A router answering every UnoService path through `service`.
        """
        router = APIRouter(tags=[SERVICE_TAG])

        @router.post(
            "/internal/product/uno/list/seat_choice",
            operation_id="UnoService_ListSeatChoice",
            response_model=ListSeatChoiceResponse,
            response_model_exclude_none=True,
            responses={"default": {"model": Status}},
        )
        async def list_seat_choice(
            request: ListSeatChoiceRequest,
        ) -> ListSeatChoiceResponse:
            return await service.list_seat_choice(
                request=request,
            )

        @router.post(
            "/internal/product/uno/play/action",
            operation_id="UnoService_PlayAction",
            response_model=PlayActionResponse,
            response_model_exclude_none=True,
            responses={"default": {"model": Status}},
        )
        async def play_action(
            request: PlayActionRequest,
        ) -> PlayActionResponse:
            return await service.play_action(
                request=request,
            )

        @router.post(
            "/internal/product/uno/read/game",
            operation_id="UnoService_ReadGame",
            response_model=ReadGameResponse,
            response_model_exclude_none=True,
            responses={"default": {"model": Status}},
        )
        async def read_game(
            request: ReadGameRequest,
        ) -> ReadGameResponse:
            return await service.read_game(
                request=request,
            )

        @router.post(
            "/internal/product/uno/read/table",
            operation_id="UnoService_ReadTable",
            response_model=ReadTableResponse,
            response_model_exclude_none=True,
            responses={"default": {"model": Status}},
        )
        async def read_table(
            request: ReadTableRequest,
        ) -> ReadTableResponse:
            return await service.read_table(
                request=request,
            )

        @router.post(
            "/internal/product/uno/start/game",
            operation_id="UnoService_StartGame",
            response_model=StartGameResponse,
            response_model_exclude_none=True,
            responses={"default": {"model": Status}},
        )
        async def start_game(
            request: StartGameRequest,
        ) -> StartGameResponse:
            return await service.start_game(
                request=request,
            )

        @router.post(
            "/internal/product/uno/take/seat",
            operation_id="UnoService_TakeSeat",
            response_model=TakeSeatResponse,
            response_model_exclude_none=True,
            responses={"default": {"model": Status}},
        )
        async def take_seat(
            request: TakeSeatRequest,
        ) -> TakeSeatResponse:
            return await service.take_seat(
                request=request,
            )

        return router
