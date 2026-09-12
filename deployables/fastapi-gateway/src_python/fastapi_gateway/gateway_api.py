"""
The gateway: a FastAPI application and the server that runs it.
"""

import asyncio
import logging

import uvicorn
from fastapi import FastAPI
from game.service.game_routers import GameRouters
from lobby.service.lobby_routers import LobbyRouters
from product_chess.service.product_chess_routers import ProductChessRouters

from fastapi_gateway.gateway_api_config import ApplicationConfig, GatewayAPIConfig, ServerConfig
from fastapi_gateway.gateway_clients import GatewayClients
from fastapi_gateway.payload_types import PayloadTypeRegistry


class GatewayAPI:
    """
    The HTTP entry point to the system.

    Serves plain HTTP. TLS is terminated ahead of this process, so a request
    reaching it has already left the network the certificate covers.

    The clients are dialled by `start`. A gRPC channel binds to the running
    event loop when it is created, and the constructor runs before there is one.
    """

    def __init__(self, config: GatewayAPIConfig) -> None:
        self._config = config

    def start(self) -> None:
        """
        Open the clients, listen until the process is asked to stop, then close
        them.
        """
        asyncio.run(self._serve())

    @staticmethod
    def build_application(config: ApplicationConfig, clients: GatewayClients) -> FastAPI:
        """
        The application, with the routers each domain publishes.

        Adding a domain is a dependency and one more line.
        """
        application = FastAPI(
            title=config.title,
            version=config.version,
            root_path=config.root_path,
        )
        application.include_router(LobbyRouters.table_service(clients.table))
        application.include_router(LobbyRouters.seat_service(clients.seat))
        application.include_router(GameRouters.session_service(clients.session))
        application.include_router(GameRouters.game_spec_service(clients.game_spec))
        application.include_router(ProductChessRouters.chess_service(clients.chess))
        return application

    async def _serve(self) -> None:
        clients = GatewayClients.unconnected()
        await clients.open(self._config.grpc)
        try:
            application = GatewayAPI.build_application(self._config.application, clients)
            server = GatewayAPI._build_server(application, self._config.server)
            logging.getLogger(self._config.application.title).info(
                "translating %d payload types", len(PayloadTypeRegistry.get_type_names())
            )
            await server.serve()
        finally:
            await clients.close()

    @staticmethod
    def _build_server(application: FastAPI, config: ServerConfig) -> uvicorn.Server:
        return uvicorn.Server(
            uvicorn.Config(
                app=application,
                host=config.host,
                port=config.port,
                log_level=config.log_level,
                access_log=config.access_log,
                proxy_headers=config.proxy_headers,
                forwarded_allow_ips=config.forwarded_allow_ips,
            )
        )
