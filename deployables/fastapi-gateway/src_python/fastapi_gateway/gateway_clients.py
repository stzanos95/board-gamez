"""
Every client this gateway calls through, opened together and closed together.
"""

from dataclasses import dataclass

from core.grpc.channel_options import ChannelOptions
from game.service.grpc_game_spec_client import GrpcGameSpecClient
from game.service.grpc_session_client import GrpcSessionClient
from lobby.service.grpc_table_client import GrpcTableClient
from product_chess.service.grpc_chess_client import GrpcChessClient

from fastapi_gateway.gateway_api_config import GrpcConfig


@dataclass(frozen=True, slots=True)
class GatewayClients:
    """
    One client per service the gateway answers by calling.

    Built unconnected by `unconnected`, so an application can be assembled
    without an event loop, and dialled by `open` once there is one.
    """

    table: GrpcTableClient
    session: GrpcSessionClient
    game_spec: GrpcGameSpecClient
    chess: GrpcChessClient

    @staticmethod
    def unconnected() -> "GatewayClients":
        return GatewayClients(
            table=GrpcTableClient(),
            session=GrpcSessionClient(),
            game_spec=GrpcGameSpecClient(),
            chess=GrpcChessClient(),
        )

    async def open(self, config: GrpcConfig) -> None:
        """
        Dial the gRPC server with every client. Each channel connects lazily, so
        this does not block.
        """
        options = GatewayClients._channel_options(config)
        await self.table.connect(config.address, options)
        await self.session.connect(config.address, options)
        await self.game_spec.connect(config.address, options)
        await self.chess.connect(config.address, options)

    async def close(self) -> None:
        await self.table.close()
        await self.session.close()
        await self.game_spec.close()
        await self.chess.close()

    @staticmethod
    def _channel_options(config: GrpcConfig) -> ChannelOptions:
        return ChannelOptions(
            max_receive_message_bytes=config.max_receive_message_bytes,
            max_send_message_bytes=config.max_send_message_bytes,
        )
