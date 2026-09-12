"""
RulesService, as the platform answers it over gRPC.

Implements the servicer the schema generates. Every method is the same three
steps: adapt the request, call the controller, adapt what comes back. No field
is read off a request here, and nothing is decided.

The method names are the schema's, not this repository's. gRPC dispatches on
them, so they keep protobuf's casing; the per-file ignore in pyproject.toml is
what lets them.
"""

import grpc
from idl.game.dto.rules_pb2 import (
    ApplyActionRequest,
    ApplyActionResponse,
    CreateGameRequest,
    CreateGameResponse,
    ExpireDeadlineRequest,
    ExpireDeadlineResponse,
    ReadBoundsRequest,
    ReadBoundsResponse,
    ReadViewRequest,
    ReadViewResponse,
    WithdrawParticipantRequest,
    WithdrawParticipantResponse,
)
from idl.game.service.rules_pb2_grpc import RulesServiceServicer

from game.adapters.rules_adapters import RulesAdapters
from game.controller.rules_controller import RulesController


class GrpcRulesService(RulesServiceServicer):
    """
    Every RulesService operation, as a gRPC call reaches the platform.
    """

    def __init__(self, controller: RulesController) -> None:
        self._controller = controller

    async def CreateGame(
        self,
        request: CreateGameRequest,
        context: grpc.aio.ServicerContext[CreateGameRequest, CreateGameResponse],
    ) -> CreateGameResponse:
        state = await self._controller.create_game(
            RulesAdapters.create_request_to_game_type(request),
            RulesAdapters.create_request_to_participant_roles(request),
            RulesAdapters.create_request_to_seed(request),
        )
        return RulesAdapters.game_state_to_create_response(state)

    async def ApplyAction(
        self,
        request: ApplyActionRequest,
        context: grpc.aio.ServicerContext[ApplyActionRequest, ApplyActionResponse],
    ) -> ApplyActionResponse:
        state = await self._controller.apply_action(
            RulesAdapters.apply_request_to_game_type(request),
            RulesAdapters.apply_request_to_state(request),
            RulesAdapters.apply_request_to_action(request),
        )
        return RulesAdapters.game_state_to_apply_response(state)

    async def ReadView(
        self,
        request: ReadViewRequest,
        context: grpc.aio.ServicerContext[ReadViewRequest, ReadViewResponse],
    ) -> ReadViewResponse:
        view = await self._controller.read_view(
            RulesAdapters.view_request_to_game_type(request),
            RulesAdapters.view_request_to_state(request),
            RulesAdapters.view_request_to_participant(request),
        )
        return RulesAdapters.view_to_view_response(view)

    async def WithdrawParticipant(
        self,
        request: WithdrawParticipantRequest,
        context: grpc.aio.ServicerContext[WithdrawParticipantRequest, WithdrawParticipantResponse],
    ) -> WithdrawParticipantResponse:
        state = await self._controller.withdraw_participant(
            RulesAdapters.withdraw_request_to_game_type(request),
            RulesAdapters.withdraw_request_to_state(request),
            RulesAdapters.withdraw_request_to_participant(request),
        )
        return RulesAdapters.game_state_to_withdraw_response(state)

    async def ExpireDeadline(
        self,
        request: ExpireDeadlineRequest,
        context: grpc.aio.ServicerContext[ExpireDeadlineRequest, ExpireDeadlineResponse],
    ) -> ExpireDeadlineResponse:
        state = await self._controller.expire_deadline(
            RulesAdapters.expire_request_to_game_type(request),
            RulesAdapters.expire_request_to_state(request),
        )
        return RulesAdapters.game_state_to_expire_response(state)

    async def ReadBounds(
        self,
        request: ReadBoundsRequest,
        context: grpc.aio.ServicerContext[ReadBoundsRequest, ReadBoundsResponse],
    ) -> ReadBoundsResponse:
        bounds = await self._controller.read_bounds(
            RulesAdapters.bounds_request_to_game_type(request)
        )
        return RulesAdapters.bounds_to_bounds_response(bounds)
