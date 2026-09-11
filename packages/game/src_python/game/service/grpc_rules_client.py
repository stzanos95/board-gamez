"""
RulesService, as it is called over gRPC.

A session controller holds one of these per game for the life of the process.
The channel it dials is opened once at bringup and closed when the process stops.

The method names the stub dispatches on are the schema's, so they keep protobuf's
casing. Nothing outside this file sees them.
"""

from typing import cast

import grpc
from core.grpc.channel_options import ChannelOptions
from google.protobuf import any_pb2
from idl.game.model.action_pb2 import Action
from idl.game.model.game_spec_pb2 import ParticipantBounds
from idl.game.model.game_state_pb2 import GameState
from idl.game.service.rules_pb2_grpc import RulesServiceAsyncStub, RulesServiceStub

from game.adapters.rules_adapters import RulesAdapters
from game.service.base_rules_client import BaseRulesClient
from game.service.rules_config import RulesUpstreamConfig


class GrpcRulesClient(BaseRulesClient):
    """
    Every RulesService operation, as a call leaves for one game's rules.

    Built unconnected, because a gRPC channel belongs to a running event loop and
    there is none while an application is being assembled. `open` is called once
    the loop is up, and `close` on the way down.
    """

    def __init__(self, config: RulesUpstreamConfig) -> None:
        self._config = config
        self._channel: grpc.aio.Channel | None = None
        self._stub: RulesServiceAsyncStub | None = None

    async def open(self) -> None:
        """
        Dial the rules. The channel connects lazily, so this does not block.
        """
        options = ChannelOptions(
            max_receive_message_bytes=self._config.max_receive_message_bytes,
            max_send_message_bytes=self._config.max_send_message_bytes,
        )
        channel = grpc.aio.insecure_channel(self._config.address, options=options.to_options())
        self._channel = channel
        # One generated class constructs a stub for either channel type. The async
        # stub names the awaitable call types an aio channel answers with.
        self._stub = cast(RulesServiceAsyncStub, RulesServiceStub(channel))

    async def close(self) -> None:
        if self._channel is not None:
            await self._channel.close()
            self._channel = None
            self._stub = None

    async def create_game(self, participant_count: int) -> GameState | None:
        response = await self._connected_stub().CreateGame(
            RulesAdapters.participant_count_to_create_request(participant_count)
        )
        return RulesAdapters.create_response_to_game_state(response)

    async def apply_action(self, state: GameState, action: Action) -> GameState | None:
        response = await self._connected_stub().ApplyAction(
            RulesAdapters.state_and_action_to_apply_request(state, action)
        )
        return RulesAdapters.apply_response_to_game_state(response)

    async def read_view(self, state: GameState, participant: int) -> any_pb2.Any:
        response = await self._connected_stub().ReadView(
            RulesAdapters.state_and_participant_to_view_request(state, participant)
        )
        return RulesAdapters.view_response_to_view(response)

    async def read_bounds(self) -> ParticipantBounds:
        response = await self._connected_stub().ReadBounds(RulesAdapters.bounds_request())
        return RulesAdapters.bounds_response_to_bounds(response)

    def _connected_stub(self) -> RulesServiceAsyncStub:
        if self._stub is None:
            raise RuntimeError(
                f"the rules client for {self._config.address} was called before open() "
                f"dialled its channel"
            )
        return self._stub
