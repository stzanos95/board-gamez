"""
The server: a gRPC server and the servicers each domain publishes.
"""

import asyncio
import logging
import signal

import grpc
from core.grpc.channel_options import ChannelOptions
from grpc_reflection.v1alpha import reflection
from lobby.controller.table_controller import TableController
from lobby.service.lobby_servicers import LobbyServicers

from grpc_server.service_host_config import ServerConfig, ServiceHostConfig

SHUTDOWN_SIGNALS = (signal.SIGINT, signal.SIGTERM)
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


class ServiceHost:
    """
    The gRPC entry point to the system.

    Serves plain HTTP/2 without TLS. Transport security is terminated ahead of
    this process, which is reachable only from inside.

    Bringup happens once, here: the server is built from the configuration, the
    servicers each domain publishes are registered on it, and `start` begins
    listening until the process is asked to stop.
    """

    def __init__(self, config: ServiceHostConfig) -> None:
        self._application = config.application
        self._server = config.server

    def start(self) -> None:
        """
        Listen until the process is asked to stop.
        """
        logging.basicConfig(level=self._server.log_level.as_logging_level, format=LOG_FORMAT)
        asyncio.run(self._serve())

    async def _serve(self) -> None:
        """
        Build, register, listen, and stop when a signal says to.

        The server is built here and not in the constructor: a gRPC async server
        binds to the running event loop, and there is none until asyncio.run has
        started one.
        """
        server = ServiceHost._build_server(self._server)
        service_names = ServiceHost._register_services(server)
        if self._server.reflection:
            reflection.enable_server_reflection([*service_names, reflection.SERVICE_NAME], server)
        address = ServiceHost._address(self._server)
        server.add_insecure_port(address)

        await server.start()
        logging.getLogger(self._application.name).info(
            "serving %d services on %s", len(service_names), address
        )
        await ServiceHost._wait_for_shutdown()
        await server.stop(self._server.graceful_shutdown_seconds)

    @staticmethod
    def _build_server(config: ServerConfig) -> grpc.aio.Server:
        options = ChannelOptions(
            max_receive_message_bytes=config.max_receive_message_bytes,
            max_send_message_bytes=config.max_send_message_bytes,
        )
        return grpc.aio.server(
            options=options.to_options(),
            maximum_concurrent_rpcs=config.maximum_concurrent_rpcs,
        )

    @staticmethod
    def _register_services(server: grpc.aio.Server) -> tuple[str, ...]:
        """
        Every servicer this process serves, and the names it serves them under.

        Each controller is built here, which is where anything it depends on will
        be built from the configuration. Adding a domain is a dependency and one
        more line.
        """
        return (LobbyServicers.add_table_service(server, TableController()),)

    @staticmethod
    def _address(config: ServerConfig) -> str:
        return f"{config.host}:{config.port}"

    @staticmethod
    async def _wait_for_shutdown() -> None:
        """
        Wait until the process is asked to stop.

        A container stops its process with a signal, so the handler is what turns
        that into a graceful shutdown rather than a killed connection.
        """
        stopping = asyncio.Event()
        loop = asyncio.get_running_loop()
        for shutdown_signal in SHUTDOWN_SIGNALS:
            loop.add_signal_handler(shutdown_signal, stopping.set)
        await stopping.wait()
