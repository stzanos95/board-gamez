"""
The server: a socketify application, the routes on it, and the sources
relayed into it.
"""

import asyncio
import functools
import logging
import signal

from core.queue.base_queue_consumer import BaseQueueConsumer
from core.queue.config import QueueConfig
from core.queue.provider import QueueProvider
from socketify import App, AppListenOptions

from websocket_server.controller.client_hub import ClientHub
from websocket_server.controller.subscription_controller import SubscriptionController
from websocket_server.service.socket_routes import LOBBY_PATH, TABLE_PATH, SocketRoutes
from websocket_server.websocket_server_config import ServerConfig, WebsocketServerConfig

SHUTDOWN_SIGNALS = (signal.SIGINT, signal.SIGTERM)
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


class WebsocketServer:
    """
    The socket entry point to the system.

    Serves plain HTTP. TLS is terminated ahead of this process.

    Bringup happens once, here: every source is built from the configuration,
    the controller is built over them, the routes are declared on the
    application, and `start` listens until the process is asked to stop.
    """

    def __init__(self, config: WebsocketServerConfig) -> None:
        self._application = config.application
        self._server = config.server
        self._sources = config.sources

    def start(self) -> None:
        """
        Listen until the process is asked to stop, then release every source.

        The library creates the asyncio loop when the application is built and
        sets it as the current one; the relays run on that loop beside the
        sockets.

        SIGTERM reaches the handler installed here, and `run` returns. SIGINT
        reaches the handler the library installs when `run` begins, which
        closes the listener and raises SystemExit. The shutdown runs on both
        paths.
        """
        logging.basicConfig(level=self._server.log_level.as_logging_level, format=LOG_FORMAT)
        controller = WebsocketServer._build_controller(self._sources)
        routes = SocketRoutes(controller)
        application = App(lifespan=False)
        application.ws(LOBBY_PATH, routes.lobby_behavior(self._server).to_dict())
        application.ws(TABLE_PATH, routes.table_behavior(self._server).to_dict())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(controller.start())
        for shutdown_signal in SHUTDOWN_SIGNALS:
            loop.add_signal_handler(shutdown_signal, application.close)
        application.listen(
            AppListenOptions(port=self._server.port, host=self._server.host),
            functools.partial(self._on_listen, self._server),
        )
        try:
            application.run()
        finally:
            loop.run_until_complete(self._on_shutdown(controller))

    @staticmethod
    def _build_controller(sources: list[QueueConfig]) -> SubscriptionController:
        """
        The controller, over one consumer per configured source.

        Raises ValueError when no source is configured: a server with nothing
        to relay would answer every socket with silence.
        """
        if not sources:
            raise ValueError("sources is empty; configure at least one queue to relay from")
        consumers: list[BaseQueueConsumer] = [
            QueueProvider.get_consumer(source) for source in sources
        ]
        return SubscriptionController(hub=ClientHub(), sources=consumers)

    async def _on_shutdown(self, controller: SubscriptionController) -> None:
        await controller.close()
        logging.getLogger(self._application.name).info("stopped; every source is closed")

    def _on_listen(self, config: ServerConfig, listen_options: AppListenOptions) -> None:
        logging.getLogger(self._application.name).info(
            "listening on %s:%d", config.host, config.port
        )
