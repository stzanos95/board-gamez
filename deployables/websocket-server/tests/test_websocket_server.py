import unittest

from core.queue.config import QueueConfig, QueueType, RedisQueueConfig

from websocket_server.log_level import LogLevel
from websocket_server.websocket_server import WebsocketServer
from websocket_server.websocket_server_config import (
    ApplicationConfig,
    ServerConfig,
    WebsocketServerConfig,
)

REDIS_SOURCE = QueueConfig(
    queue=QueueType.REDIS,
    redis_config=RedisQueueConfig(
        host="127.0.0.1", port=6379, database=0, channel_prefix="gamez-test"
    ),
)


def config_for(sources: list[QueueConfig]) -> WebsocketServerConfig:
    return WebsocketServerConfig(
        application=ApplicationConfig(name="test server", version="9.9.9"),
        server=ServerConfig(
            host="127.0.0.1",
            port=8999,
            log_level=LogLevel.WARNING,
            idle_timeout_seconds=0,
            max_payload_bytes=256,
        ),
        sources=sources,
    )


class BringupTest(unittest.TestCase):
    """
    Bringup reads the configuration and nothing else. No socket is bound and no
    event loop is started until `start` is called.
    """

    def test_a_host_is_built_without_touching_the_network(self) -> None:
        host = WebsocketServer(config=config_for([REDIS_SOURCE]))
        self.assertIsInstance(host, WebsocketServer)

    def test_a_controller_is_built_over_every_source(self) -> None:
        controller = WebsocketServer._build_controller([REDIS_SOURCE, REDIS_SOURCE])
        self.assertEqual(len(controller._sources), 2)

    def test_no_source_is_refused(self) -> None:
        with self.assertRaisesRegex(ValueError, "sources is empty"):
            WebsocketServer._build_controller([])
