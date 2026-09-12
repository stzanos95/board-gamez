"""
SeatService, generated from the OpenAPI document. Do not edit.

BaseSeatService declares one method per operation, and
SeatServiceRouter.build binds every path to an instance of it. The
implementation belongs to the domain package that owns this service.
"""

from abc import ABC, abstractmethod

from fastapi import APIRouter

from idl_fastapi.google.rpc import Status
from idl_fastapi.idl.lobby.dto import (
    LeaveTableRequest,
    LeaveTableResponse,
    VacateSeatRequest,
    VacateSeatResponse,
)


SERVICE_TAG = "SeatService"


class BaseSeatService(ABC):
    """
    What an implementation of SeatService must answer.
    """

    @abstractmethod
    async def leave_table(
        self,
        request: LeaveTableRequest,
    ) -> LeaveTableResponse:
        """
        POST /internal/platform/lobby/leave/table
        """

    @abstractmethod
    async def vacate_seat(
        self,
        request: VacateSeatRequest,
    ) -> VacateSeatResponse:
        """
        POST /internal/platform/lobby/vacate/seat
        """


class SeatServiceRouter:
    """
    The paths SeatService declares, bound to an implementation.
    """

    @staticmethod
    def build(service: BaseSeatService) -> APIRouter:
        """
        A router answering every SeatService path through `service`.
        """
        router = APIRouter(tags=[SERVICE_TAG])

        @router.post(
            "/internal/platform/lobby/leave/table",
            operation_id="SeatService_LeaveTable",
            response_model=LeaveTableResponse,
            response_model_exclude_none=True,
            responses={"default": {"model": Status}},
        )
        async def leave_table(
            request: LeaveTableRequest,
        ) -> LeaveTableResponse:
            return await service.leave_table(
                request=request,
            )

        @router.post(
            "/internal/platform/lobby/vacate/seat",
            operation_id="SeatService_VacateSeat",
            response_model=VacateSeatResponse,
            response_model_exclude_none=True,
            responses={"default": {"model": Status}},
        )
        async def vacate_seat(
            request: VacateSeatRequest,
        ) -> VacateSeatResponse:
            return await service.vacate_seat(
                request=request,
            )

        return router
