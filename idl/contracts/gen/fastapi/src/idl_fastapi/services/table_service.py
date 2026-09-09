"""
TableService, generated from the OpenAPI document. Do not edit.

BaseTableService declares one method per operation, and
TableServiceRouter.build binds every path to an instance of it. The
implementation belongs to the domain package that owns this service.
"""

from abc import ABC, abstractmethod

from fastapi import APIRouter

from idl_fastapi.google.rpc import Status
from idl_fastapi.idl.lobby.dto import (
    DeleteTableRequest,
    DeleteTableResponse,
    ListTableRequest,
    ListTableResponse,
    ReadTableRequest,
    ReadTableResponse,
    UpsertTableRequest,
    UpsertTableResponse,
)


SERVICE_TAG = "TableService"


class BaseTableService(ABC):
    """
    What an implementation of TableService must answer.
    """

    @abstractmethod
    async def delete_table(
        self,
        request: DeleteTableRequest,
    ) -> DeleteTableResponse:
        """
        POST /internal/platform/lobby/delete/table
        """

    @abstractmethod
    async def list_table(
        self,
        request: ListTableRequest,
    ) -> ListTableResponse:
        """
        POST /internal/platform/lobby/list/table
        """

    @abstractmethod
    async def read_table(
        self,
        request: ReadTableRequest,
    ) -> ReadTableResponse:
        """
        POST /internal/platform/lobby/read/table
        """

    @abstractmethod
    async def upsert_table(
        self,
        request: UpsertTableRequest,
    ) -> UpsertTableResponse:
        """
        POST /internal/platform/lobby/upsert/table
        """


class TableServiceRouter:
    """
    The paths TableService declares, bound to an implementation.
    """

    @staticmethod
    def build(service: BaseTableService) -> APIRouter:
        """
        A router answering every TableService path through `service`.
        """
        router = APIRouter(tags=[SERVICE_TAG])

        @router.post(
            "/internal/platform/lobby/delete/table",
            operation_id="TableService_DeleteTable",
            response_model=DeleteTableResponse,
            response_model_exclude_none=True,
            responses={"default": {"model": Status}},
        )
        async def delete_table(
            request: DeleteTableRequest,
        ) -> DeleteTableResponse:
            return await service.delete_table(
                request=request,
            )

        @router.post(
            "/internal/platform/lobby/list/table",
            operation_id="TableService_ListTable",
            response_model=ListTableResponse,
            response_model_exclude_none=True,
            responses={"default": {"model": Status}},
        )
        async def list_table(
            request: ListTableRequest,
        ) -> ListTableResponse:
            return await service.list_table(
                request=request,
            )

        @router.post(
            "/internal/platform/lobby/read/table",
            operation_id="TableService_ReadTable",
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
            "/internal/platform/lobby/upsert/table",
            operation_id="TableService_UpsertTable",
            response_model=UpsertTableResponse,
            response_model_exclude_none=True,
            responses={"default": {"model": Status}},
        )
        async def upsert_table(
            request: UpsertTableRequest,
        ) -> UpsertTableResponse:
            return await service.upsert_table(
                request=request,
            )

        return router
