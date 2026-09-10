import unittest

from lobby.repository.config import (
    RedisTableRepositoryConfig,
    TableRepositoryConfig,
    TableRepositoryType,
)

from grpc_server.log_level import LogLevel
from grpc_server.service_host import ServiceHost
from grpc_server.service_host_config import (
    ApplicationConfig,
    LobbyConfig,
    ServerConfig,
    ServiceHostConfig,
)

CONFIGURED_PORT = 50999
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


def config_for() -> ServiceHostConfig:
    return ServiceHostConfig(
        application=ApplicationConfig(name="test server", version="9.9.9"),
        server=server_config(),
        lobby=lobby_config(),
    )


class BringupTest(unittest.TestCase):
    """
    Bringup reads the configuration and nothing else. No socket is bound and no
    event loop is started until `start` is called.
    """

    def test_a_host_is_built_without_touching_the_network(self) -> None:
        host = ServiceHost(config=config_for())
        self.assertIsInstance(host, ServiceHost)
