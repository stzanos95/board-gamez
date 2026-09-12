import unittest

import grpc
from core.clock.system_clock import SystemClock
from core.queue.config import QueueConfig, QueueType, RedisQueueConfig
from core.queue.provider import QueueProvider
from game.repository.config import (
    RedisSessionRepositoryConfig,
    SessionRepositoryConfig,
    SessionRepositoryType,
)
from lobby.repository.config import (
    RedisTableRepositoryConfig,
    TableRepositoryConfig,
    TableRepositoryType,
)

from grpc_server.log_level import LogLevel
from grpc_server.products.hosted_products import HostedProducts
from grpc_server.service_host import ServiceHost
from grpc_server.service_host_config import (
    ApplicationConfig,
    DeadlineConfig,
    GameConfig,
    LobbyConfig,
    ServerConfig,
    ServiceHostConfig,
)

CONFIGURED_PORT = 50999
POLL_INTERVAL_SECONDS = 0.5
REDIS_PORT = 6379
REDIS_DATABASE = 0
RECEIVE_LIMIT = 1024
SEND_LIMIT = 2048


def server_config() -> ServerConfig:
    return ServerConfig(
        host="127.0.0.1",
        port=CONFIGURED_PORT,
        log_level=LogLevel.WARNING,
        maximum_concurrent_rpcs=8,
        max_receive_message_bytes=RECEIVE_LIMIT,
        max_send_message_bytes=SEND_LIMIT,
        graceful_shutdown_seconds=3,
        reflection=False,
    )


def lobby_config() -> LobbyConfig:
    return LobbyConfig(
        table_repository=TableRepositoryConfig(
            repository=TableRepositoryType.REDIS,
            redis_config=RedisTableRepositoryConfig(
                host="127.0.0.1",
                port=REDIS_PORT,
                database=REDIS_DATABASE,
                key_prefix="board-gamez-test",
            ),
        )
    )


def game_config() -> GameConfig:
    return GameConfig(
        session_repository=SessionRepositoryConfig(
            repository=SessionRepositoryType.REDIS,
            redis_config=RedisSessionRepositoryConfig(
                host="127.0.0.1",
                port=REDIS_PORT,
                database=REDIS_DATABASE,
                key_prefix="board-gamez-test",
            ),
        ),
        deadlines=DeadlineConfig(poll_interval_seconds=POLL_INTERVAL_SECONDS),
    )


def queue_config() -> QueueConfig:
    return QueueConfig(
        queue=QueueType.REDIS,
        redis_config=RedisQueueConfig(
            host="127.0.0.1", port=REDIS_PORT, database=REDIS_DATABASE, channel_prefix="gamez-test"
        ),
    )


def config_for() -> ServiceHostConfig:
    return ServiceHostConfig(
        application=ApplicationConfig(name="test server", version="9.9.9"),
        server=server_config(),
        lobby=lobby_config(),
        game=game_config(),
        queue=queue_config(),
    )


class BringupTest(unittest.TestCase):
    """
    Bringup reads the configuration and nothing else. No socket is bound and no
    event loop is started until `start` is called.
    """

    def test_a_host_is_built_without_touching_the_network(self) -> None:
        host = ServiceHost(config=config_for())
        self.assertIsInstance(host, ServiceHost)


class RegistrationTest(unittest.IsolatedAsyncioTestCase):
    """
    Registration builds every controller from the configuration and names every
    service, without a store or a port being reached.
    """

    async def test_every_service_is_registered_under_its_full_name(self) -> None:
        server = grpc.aio.server()
        products = HostedProducts.build()
        controllers = ServiceHost._build_controllers(
            lobby_config(),
            game_config(),
            QueueProvider.get_publisher(queue_config()),
            SystemClock(),
            products,
        )
        names = ServiceHost._register_services(server, controllers, products)
        self.assertEqual(
            names,
            (
                "idl.lobby.service.TableService",
                "idl.lobby.service.SeatService",
                "idl.game.service.SessionService",
                "idl.game.service.GameSpecService",
                "idl.game.service.RulesService",
                "idl.chess.service.ChessService",
                "idl.uno.service.UnoService",
            ),
        )
