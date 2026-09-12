"""
Every client this gateway calls through, opened together and closed together.
"""

from dataclasses import dataclass

from core.grpc.channel_options import ChannelOptions
from game.service.grpc_game_spec_client import GrpcGameSpecClient
from game.service.grpc_session_client import GrpcSessionClient
from lobby.service.grpc_seat_client import GrpcSeatClient
from lobby.service.grpc_table_client import GrpcTableClient

from fastapi_gateway.gateway_api_config import GrpcConfig
from fastapi_gateway.products.base_gateway_product import BaseGatewayProduct


@dataclass(frozen=True, slots=True)
class GatewayClients:
    """
    One client per platform service the gateway answers by calling, and every
    product served, each holding the clients of its own.

    Built unconnected by `unconnected`, so an application can be assembled
    without an event loop, and dialled by `open` once there is one.
    """

    table: GrpcTableClient
    seat: GrpcSeatClient
    session: GrpcSessionClient
    game_spec: GrpcGameSpecClient
    products: tuple[BaseGatewayProduct, ...]

    @staticmethod
    def unconnected(products: tuple[BaseGatewayProduct, ...]) -> "GatewayClients":
        return GatewayClients(
            table=GrpcTableClient(),
            seat=GrpcSeatClient(),
            session=GrpcSessionClient(),
            game_spec=GrpcGameSpecClient(),
            products=products,
        )

    async def open(self, config: GrpcConfig) -> None:
        """
        Dial the gRPC server with every client. Each channel connects lazily, so
        this does not block.
        """
        options = GatewayClients._channel_options(config)
        await self.table.connect(config.address, options)
        await self.seat.connect(config.address, options)
        await self.session.connect(config.address, options)
        await self.game_spec.connect(config.address, options)
        for product in self.products:
            await product.connect(config.address, options)

    async def close(self) -> None:
        await self.table.close()
        await self.seat.close()
        await self.session.close()
        await self.game_spec.close()
        for product in self.products:
            await product.close()

    @staticmethod
    def _channel_options(config: GrpcConfig) -> ChannelOptions:
        return ChannelOptions(
            max_receive_message_bytes=config.max_receive_message_bytes,
            max_send_message_bytes=config.max_send_message_bytes,
        )
