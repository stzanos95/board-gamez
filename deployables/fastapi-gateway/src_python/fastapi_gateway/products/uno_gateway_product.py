"""
UNO, as this gateway serves it.
"""

from core.grpc.channel_options import ChannelOptions
from fastapi import APIRouter
from google.protobuf.descriptor import FileDescriptor
from idl.uno.model import action_pb2, game_pb2, view_pb2
from product_uno.service.grpc_uno_client import GrpcUnoClient
from product_uno.service.product_uno_routers import ProductUnoRouters

from fastapi_gateway.products.base_gateway_product import BaseGatewayProduct


class UnoGatewayProduct(BaseGatewayProduct):
    """
    The UnoService paths, the client they call the platform through, and the
    types UNO packs: an action, a game, and a viewer's projection of one.
    """

    def __init__(self) -> None:
        self._client = GrpcUnoClient()

    async def connect(self, address: str, options: ChannelOptions) -> None:
        await self._client.connect(address, options)

    async def close(self) -> None:
        await self._client.close()

    def get_router(self) -> APIRouter:
        return ProductUnoRouters.uno_service(self._client)

    def get_payload_files(self) -> tuple[FileDescriptor, ...]:
        return (action_pb2.DESCRIPTOR, game_pb2.DESCRIPTOR, view_pb2.DESCRIPTOR)
