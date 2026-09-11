"""
SessionService, generated from the OpenAPI document. Do not edit.

BaseSessionService declares one method per operation, and
SessionServiceRouter.build binds every path to an instance of it. The
implementation belongs to the domain package that owns this service.
"""

from abc import ABC, abstractmethod

from fastapi import APIRouter

from idl_fastapi.google.rpc import Status
from idl_fastapi.idl.game.dto import (
    ApplyCommandRequest,
    ApplyCommandResponse,
    CreateSessionRequest,
    CreateSessionResponse,
    ReadSessionRequest,
    ReadSessionResponse,
)


SERVICE_TAG = "SessionService"


class BaseSessionService(ABC):
    """
    What an implementation of SessionService must answer.
    """

    @abstractmethod
    async def apply_command(
        self,
        request: ApplyCommandRequest,
    ) -> ApplyCommandResponse:
        """
        POST /internal/platform/game/apply/command
        """

    @abstractmethod
    async def create_session(
        self,
        request: CreateSessionRequest,
    ) -> CreateSessionResponse:
        """
        POST /internal/platform/game/create/session
        """

    @abstractmethod
    async def read_session(
        self,
        request: ReadSessionRequest,
    ) -> ReadSessionResponse:
        """
        POST /internal/platform/game/read/session
        """


class SessionServiceRouter:
    """
    The paths SessionService declares, bound to an implementation.
    """

    @staticmethod
    def build(service: BaseSessionService) -> APIRouter:
        """
        A router answering every SessionService path through `service`.
        """
        router = APIRouter(tags=[SERVICE_TAG])

        @router.post(
            "/internal/platform/game/apply/command",
            operation_id="SessionService_ApplyCommand",
            response_model=ApplyCommandResponse,
            response_model_exclude_none=True,
            responses={"default": {"model": Status}},
        )
        async def apply_command(
            request: ApplyCommandRequest,
        ) -> ApplyCommandResponse:
            return await service.apply_command(
                request=request,
            )

        @router.post(
            "/internal/platform/game/create/session",
            operation_id="SessionService_CreateSession",
            response_model=CreateSessionResponse,
            response_model_exclude_none=True,
            responses={"default": {"model": Status}},
        )
        async def create_session(
            request: CreateSessionRequest,
        ) -> CreateSessionResponse:
            return await service.create_session(
                request=request,
            )

        @router.post(
            "/internal/platform/game/read/session",
            operation_id="SessionService_ReadSession",
            response_model=ReadSessionResponse,
            response_model_exclude_none=True,
            responses={"default": {"model": Status}},
        )
        async def read_session(
            request: ReadSessionRequest,
        ) -> ReadSessionResponse:
            return await service.read_session(
                request=request,
            )

        return router
