"""
The routers the game domain serves over HTTP.

An app includes these; it builds no binding of its own. Whatever a router needs
arrives as an argument, so nothing here reads configuration.
"""

from fastapi import APIRouter
from idl_fastapi.services.game_spec_service import GameSpecServiceRouter
from idl_fastapi.services.session_service import SessionServiceRouter

from game.service.grpc_game_spec_client import GrpcGameSpecClient
from game.service.grpc_session_client import GrpcSessionClient
from game.service.http_game_spec_service import HttpGameSpecService
from game.service.http_session_service import HttpSessionService


class GameRouters:
    """
    One method per service this domain answers over HTTP.
    """

    @staticmethod
    def session_service(client: GrpcSessionClient) -> APIRouter:
        """
        The SessionService paths, declared by the schema and answered over HTTP.
        """
        return SessionServiceRouter.build(HttpSessionService(client=client))

    @staticmethod
    def game_spec_service(client: GrpcGameSpecClient) -> APIRouter:
        """
        The GameSpecService paths, declared by the schema and answered over HTTP.
        """
        return GameSpecServiceRouter.build(HttpGameSpecService(client=client))
