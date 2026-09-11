"""
RulesService, as chess answers it over gRPC.

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
    ReadBoundsRequest,
    ReadBoundsResponse,
    ReadViewRequest,
    ReadViewResponse,
)
from idl.game.service.rules_pb2_grpc import RulesServiceServicer

from product_chess.adapters.chess_rules_adapters import ChessRulesAdapters
from product_chess.controller.chess_rules import ChessRules


class GrpcRulesService(RulesServiceServicer):
    """
    Every RulesService operation, as a gRPC call reaches chess.
    """

    def __init__(self, rules: ChessRules) -> None:
        self._rules = rules

    async def CreateGame(
        self,
        request: CreateGameRequest,
        context: grpc.aio.ServicerContext[CreateGameRequest, CreateGameResponse],
    ) -> CreateGameResponse:
        state = await self._rules.create_game(
            ChessRulesAdapters.create_request_to_participant_count(request)
        )
        return ChessRulesAdapters.game_state_to_create_response(state)

    async def ApplyAction(
        self,
        request: ApplyActionRequest,
        context: grpc.aio.ServicerContext[ApplyActionRequest, ApplyActionResponse],
    ) -> ApplyActionResponse:
        state = await self._rules.apply_action(
            ChessRulesAdapters.apply_request_to_state(request),
            ChessRulesAdapters.apply_request_to_action(request),
        )
        return ChessRulesAdapters.game_state_to_apply_response(state)

    async def ReadView(
        self,
        request: ReadViewRequest,
        context: grpc.aio.ServicerContext[ReadViewRequest, ReadViewResponse],
    ) -> ReadViewResponse:
        view = await self._rules.read_view(
            ChessRulesAdapters.view_request_to_state(request),
            ChessRulesAdapters.view_request_to_participant(request),
        )
        return ChessRulesAdapters.view_to_view_response(view)

    async def ReadBounds(
        self,
        request: ReadBoundsRequest,
        context: grpc.aio.ServicerContext[ReadBoundsRequest, ReadBoundsResponse],
    ) -> ReadBoundsResponse:
        return ChessRulesAdapters.bounds_to_bounds_response(await self._rules.read_bounds())
