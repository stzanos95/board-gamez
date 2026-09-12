"""
RulesService, as UNO answers it over gRPC.

Implements the servicer the schema generates. Every method is the same three
steps: adapt the request, call the rules, adapt what comes back. No field is
read off a request here, and nothing is decided.

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

from product_uno.adapters.uno_rules_adapters import UnoRulesAdapters
from product_uno.controller.uno_rules import UnoRules


class GrpcRulesService(RulesServiceServicer):
    """
    Every RulesService operation, as a gRPC call reaches UNO.
    """

    def __init__(self, rules: UnoRules) -> None:
        self._rules = rules

    async def CreateGame(
        self,
        request: CreateGameRequest,
        context: grpc.aio.ServicerContext[CreateGameRequest, CreateGameResponse],
    ) -> CreateGameResponse:
        state = await self._rules.create_game(
            UnoRulesAdapters.create_request_to_participant_roles(request),
            UnoRulesAdapters.create_request_to_seed(request),
        )
        return UnoRulesAdapters.game_state_to_create_response(state)

    async def ApplyAction(
        self,
        request: ApplyActionRequest,
        context: grpc.aio.ServicerContext[ApplyActionRequest, ApplyActionResponse],
    ) -> ApplyActionResponse:
        state = await self._rules.apply_action(
            UnoRulesAdapters.apply_request_to_state(request),
            UnoRulesAdapters.apply_request_to_action(request),
        )
        return UnoRulesAdapters.game_state_to_apply_response(state)

    async def WithdrawParticipant(
        self,
        request: WithdrawParticipantRequest,
        context: grpc.aio.ServicerContext[WithdrawParticipantRequest, WithdrawParticipantResponse],
    ) -> WithdrawParticipantResponse:
        state = await self._rules.withdraw_participant(
            UnoRulesAdapters.withdraw_request_to_state(request),
            UnoRulesAdapters.withdraw_request_to_participant(request),
        )
        return UnoRulesAdapters.game_state_to_withdraw_response(state)

    async def ExpireDeadline(
        self,
        request: ExpireDeadlineRequest,
        context: grpc.aio.ServicerContext[ExpireDeadlineRequest, ExpireDeadlineResponse],
    ) -> ExpireDeadlineResponse:
        state = await self._rules.expire_deadline(UnoRulesAdapters.expire_request_to_state(request))
        return UnoRulesAdapters.game_state_to_expire_response(state)

    async def ReadView(
        self,
        request: ReadViewRequest,
        context: grpc.aio.ServicerContext[ReadViewRequest, ReadViewResponse],
    ) -> ReadViewResponse:
        view = await self._rules.read_view(
            UnoRulesAdapters.view_request_to_state(request),
            UnoRulesAdapters.view_request_to_participant(request),
        )
        return UnoRulesAdapters.view_to_view_response(view)

    async def ReadBounds(
        self,
        request: ReadBoundsRequest,
        context: grpc.aio.ServicerContext[ReadBoundsRequest, ReadBoundsResponse],
    ) -> ReadBoundsResponse:
        return UnoRulesAdapters.bounds_to_bounds_response(await self._rules.read_bounds())
