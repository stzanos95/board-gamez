"""
ChessService, generated from the OpenAPI document. Do not edit.

BaseChessService declares one method per operation, and
ChessServiceRouter.build binds every path to an instance of it. The
implementation belongs to the domain package that owns this service.
"""

from abc import ABC, abstractmethod

from fastapi import APIRouter

from idl_fastapi.google.rpc import Status
from idl_fastapi.idl.chess.dto import (
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


SERVICE_TAG = "ChessService"


class BaseChessService(ABC):
    """
    What an implementation of ChessService must answer.
    """

    @abstractmethod
    async def list_seat_choice(
        self,
        request: ListSeatChoiceRequest,
    ) -> ListSeatChoiceResponse:
        """
        POST /internal/product/chess/list/seat_choice
        """

    @abstractmethod
    async def play_action(
        self,
        request: PlayActionRequest,
    ) -> PlayActionResponse:
        """
        POST /internal/product/chess/play/action
        """

    @abstractmethod
    async def read_game(
        self,
        request: ReadGameRequest,
    ) -> ReadGameResponse:
        """
        POST /internal/product/chess/read/game
        """

    @abstractmethod
    async def read_table(
        self,
        request: ReadTableRequest,
    ) -> ReadTableResponse:
        """
        POST /internal/product/chess/read/table
        """

    @abstractmethod
    async def start_game(
        self,
        request: StartGameRequest,
    ) -> StartGameResponse:
        """
        POST /internal/product/chess/start/game
        """

    @abstractmethod
    async def take_seat(
        self,
        request: TakeSeatRequest,
    ) -> TakeSeatResponse:
        """
        POST /internal/product/chess/take/seat
        """


class ChessServiceRouter:
    """
    The paths ChessService declares, bound to an implementation.
    """

    @staticmethod
    def build(service: BaseChessService) -> APIRouter:
        """
        A router answering every ChessService path through `service`.
        """
        router = APIRouter(tags=[SERVICE_TAG])

        @router.post(
            "/internal/product/chess/list/seat_choice",
            operation_id="ChessService_ListSeatChoice",
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
            "/internal/product/chess/play/action",
            operation_id="ChessService_PlayAction",
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
            "/internal/product/chess/read/game",
            operation_id="ChessService_ReadGame",
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
            "/internal/product/chess/read/table",
            operation_id="ChessService_ReadTable",
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
            "/internal/product/chess/start/game",
            operation_id="ChessService_StartGame",
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
            "/internal/product/chess/take/seat",
            operation_id="ChessService_TakeSeat",
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
