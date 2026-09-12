"""
Every game this gateway serves.
"""

from fastapi_gateway.products.base_gateway_product import BaseGatewayProduct
from fastapi_gateway.products.chess_gateway_product import ChessGatewayProduct
from fastapi_gateway.products.uno_gateway_product import UnoGatewayProduct


class GatewayProducts:
    """
    The products built at bringup. Adding a game is one entry here and a
    dependency in pyproject.toml.
    """

    @staticmethod
    def build() -> tuple[BaseGatewayProduct, ...]:
        return (ChessGatewayProduct(), UnoGatewayProduct())
