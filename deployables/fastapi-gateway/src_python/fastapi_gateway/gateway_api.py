"""
The gateway: a FastAPI application and the server that runs it.
"""

import uvicorn
from fastapi import FastAPI
from lobby.service.lobby_routers import LobbyRouters

from fastapi_gateway.gateway_api_config import ApplicationConfig, GatewayAPIConfig, ServerConfig


class GatewayAPI:
    """
    The HTTP entry point to the system.

    Serves plain HTTP. TLS is terminated ahead of this process, so a request
    reaching it has already left the network the certificate covers.

    Bringup happens once, here: the application is built with the routers each
    domain publishes, the server is built around it, and `start` begins
    listening.
    """

    def __init__(self, config: GatewayAPIConfig) -> None:
        self._application = GatewayAPI._build_application(config.application)
        self._server = GatewayAPI._build_server(self._application, config.server)

    @property
    def application(self) -> FastAPI:
        """
        The ASGI application the server runs.
        """
        return self._application

    def start(self) -> None:
        """
        Listen until the process is asked to stop.
        """
        self._server.run()

    @staticmethod
    def _build_application(config: ApplicationConfig) -> FastAPI:
        application = FastAPI(
            title=config.title,
            version=config.version,
            root_path=config.root_path,
        )
        application.include_router(LobbyRouters.table_service())
        return application

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
