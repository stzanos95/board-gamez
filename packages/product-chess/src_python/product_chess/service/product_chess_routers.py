"""
The routers chess serves over HTTP.

An app includes these; it builds no binding of its own. Whatever a router needs
arrives as an argument, so nothing here reads configuration.
"""

from fastapi import APIRouter
from idl_fastapi.services.chess_service import ChessServiceRouter

from product_chess.service.grpc_chess_client import GrpcChessClient
from product_chess.service.http_chess_service import HttpChessService


class ProductChessRouters:
    """
    One method per service this product answers over HTTP.
    """

    @staticmethod
    def chess_service(client: GrpcChessClient) -> APIRouter:
        """
        The ChessService paths, declared by the schema and answered over HTTP.
        """
        return ChessServiceRouter.build(HttpChessService(client=client))
