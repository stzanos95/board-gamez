"""
Every game this process hosts.
"""

from grpc_server.products.base_hosted_product import BaseHostedProduct
from grpc_server.products.chess_hosted_product import ChessHostedProduct
from grpc_server.products.uno_hosted_product import UnoHostedProduct


class HostedProducts:
    """
    The products built at bringup. Adding a game is one entry here and a
    dependency in pyproject.toml.
    """

    @staticmethod
    def build() -> tuple[BaseHostedProduct, ...]:
        return (ChessHostedProduct(), UnoHostedProduct())
