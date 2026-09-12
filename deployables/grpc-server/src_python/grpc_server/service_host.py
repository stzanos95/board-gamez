"""
The server: a gRPC server, the servicers each domain publishes, and the tick
that expires a game's deadline.
"""

import asyncio
import logging
import signal

import grpc
from core.clock.base_clock import BaseClock
from core.clock.system_clock import SystemClock
from core.grpc.channel_options import ChannelOptions
from core.queue.base_queue_publisher import BaseQueuePublisher
from core.queue.provider import QueueProvider
from game.controller.game_spec_controller import GameSpecController
from game.controller.rules_registry import RulesRegistry
from game.controller.session_controller import SessionController
from game.repository.provider import SessionRepositoryProvider
from game.service.deadline_ticker import DeadlineTicker
from game.service.game_servicers import GameServicers
from grpc_reflection.v1alpha import reflection
from lobby.controller.seat_controller import SeatController
from lobby.controller.seating_registry import SeatingRegistry
from lobby.controller.table_controller import TableController
from lobby.repository.provider import TableRepositoryProvider
from lobby.service.lobby_servicers import LobbyServicers

from grpc_server.platform_controllers import PlatformControllers
from grpc_server.products.base_hosted_product import BaseHostedProduct
from grpc_server.products.hosted_products import HostedProducts
from grpc_server.service_host_config import (
    GameConfig,
    LobbyConfig,
    ServerConfig,
    ServiceHostConfig,
)

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
        self._lobby = config.lobby
        self._game = config.game
        self._queue = config.queue

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
        queue_publisher = QueueProvider.get_publisher(self._queue)
        products = HostedProducts.build()
        controllers = ServiceHost._build_controllers(
            self._lobby, self._game, queue_publisher, SystemClock(), products
        )
        service_names = ServiceHost._register_services(server, controllers, products)
        if self._server.reflection:
            reflection.enable_server_reflection([*service_names, reflection.SERVICE_NAME], server)
        address = ServiceHost._address(self._server)
        server.add_insecure_port(address)
        ticker = DeadlineTicker(
            sessions=controllers.sessions,
            interval_seconds=self._game.deadlines.poll_interval_seconds,
        )
        stopping = ServiceHost._stopping_on_signal()

        await server.start()
        ticking = asyncio.create_task(ticker.run(stopping))
        logging.getLogger(self._application.name).info(
            "serving %d services on %s", len(service_names), address
        )
        await stopping.wait()
        await server.stop(self._server.graceful_shutdown_seconds)
        await ticking
        await queue_publisher.close()

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
    def _build_controllers(
        lobby: LobbyConfig,
        game: GameConfig,
        queue_publisher: BaseQueuePublisher,
        clock: BaseClock,
        products: tuple[BaseHostedProduct, ...],
    ) -> PlatformControllers:
        """
        Each platform controller and everything it depends on, built from the
        configuration. Adding a domain is a dependency and one more field.

        Every product's rules are held in-process: the session controller
        calls them directly, and the same object answers RulesService for a
        tool that reaches it through this server.
        """
        table_repository = TableRepositoryProvider.get_table_repository(lobby.table_repository)
        session_repository = SessionRepositoryProvider.get_session_repository(
            game.session_repository
        )
        rules = RulesRegistry(
            {product.get_game_type(): product.get_rules() for product in products}
        )
        seating = SeatingRegistry(
            {product.get_game_type(): product.get_seating() for product in products}
        )
        tables = TableController(repository=table_repository, queue_publisher=queue_publisher)
        sessions = SessionController(
            repository=session_repository,
            rules=rules,
            queue_publisher=queue_publisher,
            clock=clock,
        )
        seats = SeatController(
            tables=tables,
            seating=seating,
            sessions=sessions,
            rules=rules,
            queue_publisher=queue_publisher,
        )
        return PlatformControllers(
            tables=tables,
            seats=seats,
            sessions=sessions,
            game_specs=GameSpecController(rules=rules),
        )

    @staticmethod
    def _register_services(
        server: grpc.aio.Server,
        controllers: PlatformControllers,
        products: tuple[BaseHostedProduct, ...],
    ) -> tuple[str, ...]:
        """
        Every servicer this process serves, and the names it serves them under:
        the platform's, then each product's.
        """
        platform_names = (
            LobbyServicers.add_table_service(server, controllers.tables),
            LobbyServicers.add_seat_service(server, controllers.seats),
            GameServicers.add_session_service(server, controllers.sessions),
            GameServicers.add_game_spec_service(server, controllers.game_specs),
        )
        product_names = tuple(
            name for product in products for name in product.add_servicers(server, controllers)
        )
        return platform_names + product_names

    @staticmethod
    def _address(config: ServerConfig) -> str:
        return f"{config.host}:{config.port}"

    @staticmethod
    def _stopping_on_signal() -> asyncio.Event:
        """
        An event set when the process is asked to stop.

        A container stops its process with a signal, so the handler is what turns
        that into a graceful shutdown rather than a killed connection.
        """
        stopping = asyncio.Event()
        loop = asyncio.get_running_loop()
        for shutdown_signal in SHUTDOWN_SIGNALS:
            loop.add_signal_handler(shutdown_signal, stopping.set)
        return stopping
