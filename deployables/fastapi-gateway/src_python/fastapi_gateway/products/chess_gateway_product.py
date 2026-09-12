"""
Chess, as this gateway serves it.
"""

from core.grpc.channel_options import ChannelOptions
from fastapi import APIRouter
from google.protobuf.descriptor import FileDescriptor
from idl.chess.model import action_pb2, game_pb2, side_pb2
from product_chess.service.grpc_chess_client import GrpcChessClient
from product_chess.service.product_chess_routers import ProductChessRouters

from fastapi_gateway.products.base_gateway_product import BaseGatewayProduct


class ChessGatewayProduct(BaseGatewayProduct):
    """
    The ChessService paths, the client they call the platform through, and
    the types chess packs: an action, a game, and a seat's side.
    """

    def __init__(self) -> None:
        self._client = GrpcChessClient()

    async def connect(self, address: str, options: ChannelOptions) -> None:
        await self._client.connect(address, options)

    async def close(self) -> None:
        await self._client.close()

    def get_router(self) -> APIRouter:
        return ProductChessRouters.chess_service(self._client)

    def get_payload_files(self) -> tuple[FileDescriptor, ...]:
        return (action_pb2.DESCRIPTOR, game_pb2.DESCRIPTOR, side_pb2.DESCRIPTOR)
