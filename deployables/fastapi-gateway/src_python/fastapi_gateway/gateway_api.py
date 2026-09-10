"""
The gateway: a FastAPI application and the server that runs it.
"""

import asyncio

import uvicorn
from core.grpc.channel_options import ChannelOptions
from fastapi import FastAPI
from lobby.service.grpc_table_client import GrpcTableClient
from lobby.service.lobby_routers import LobbyRouters

from fastapi_gateway.gateway_api_config import (
    ApplicationConfig,
    GatewayAPIConfig,
    GrpcConfig,
    ServerConfig,
)


class GatewayAPI:
    """
    The HTTP entry point to the system.

    Serves plain HTTP. TLS is terminated ahead of this process, so a request
    reaching it has already left the network the certificate covers.

    A client is absent until `start` opens it. A gRPC channel binds to the
    running event loop when it is created, and the constructor runs before there
    is one.
    """

    def __init__(self, config: GatewayAPIConfig) -> None:
        self._config = config
        self._table_client: GrpcTableClient | None = None

    def start(self) -> None:
        """
        Open the clients, listen until the process is asked to stop, then close
        them.
        """
        asyncio.run(self._serve())

    @staticmethod
    def build_application(config: ApplicationConfig, table_client: GrpcTableClient) -> FastAPI:
        """
        The application, with the routers each domain publishes.

        Adding a domain is a dependency and one more line.
        """
        application = FastAPI(
            title=config.title,
            version=config.version,
            root_path=config.root_path,
        )
        application.include_router(LobbyRouters.table_service(table_client))
        return application

    async def _serve(self) -> None:
        await self._open_clients()
        try:
            application = GatewayAPI.build_application(
                self._config.application, self._require_table_client()
            )
            server = GatewayAPI._build_server(application, self._config.server)
            await server.serve()
        finally:
            await self._close_clients()

    async def _open_clients(self) -> None:
        """
        Dial every upstream. Each channel connects lazily, so this does not block.
        """
        upstream = self._config.upstreams.lobby
        client = GrpcTableClient()
        await client.connect(upstream.address, GatewayAPI._channel_options(upstream))
        self._table_client = client

    async def _close_clients(self) -> None:
        if self._table_client is not None:
            await self._table_client.close()
            self._table_client = None

    def _require_table_client(self) -> GrpcTableClient:
        if self._table_client is None:
            raise RuntimeError("the table client is used before start() opened it")
        return self._table_client

    @staticmethod
    def _channel_options(config: GrpcConfig) -> ChannelOptions:
        return ChannelOptions(
            max_receive_message_bytes=config.max_receive_message_bytes,
            max_send_message_bytes=config.max_send_message_bytes,
        )

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
