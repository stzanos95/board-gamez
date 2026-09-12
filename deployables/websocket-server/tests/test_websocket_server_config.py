import unittest
from pathlib import Path

from core.queue.config import QueueType

from websocket_server.log_level import LogLevel
from websocket_server.websocket_server_config import ApplicationConfig, WebsocketServerConfig

SHIPPED_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "websocket_server.yaml"
CONTAINER_CONFIG_PATH = (
    Path(__file__).resolve().parent.parent / "config" / "websocket_server.container.yaml"
)

SHIPPED_PORT = 8082
IDLE_TIMEOUT = 30
MAX_PAYLOAD = 512

COMPLETE_CONFIG = """
application:
  name: test server
  version: "9.9.9"
server:
  host: "127.0.0.1"
  port: 8999
  log_level: warning
  idle_timeout_seconds: 30
  max_payload_bytes: 512
sources:
  - queue: redis
    redis_config:
      host: "127.0.0.1"
      port: 6379
      database: 0
      channel_prefix: "gamez-test"
  - queue: kafka
    kafka_config:
      bootstrap_servers: "broker:9092"
"""


class ReadingSettingsTest(unittest.TestCase):
    def test_the_shipped_configuration_parses(self) -> None:
        config = WebsocketServerConfig.from_yaml(SHIPPED_CONFIG_PATH.read_text(encoding="utf-8"))
        self.assertEqual(config.server.port, SHIPPED_PORT)
        self.assertIs(config.server.log_level, LogLevel.INFO)
        self.assertEqual(len(config.sources), 1)
        self.assertIs(config.sources[0].queue, QueueType.REDIS)
        self.assertIsNotNone(config.sources[0].redis_config)

    def test_the_container_configuration_differs_only_in_the_broker_host(self) -> None:
        shipped = WebsocketServerConfig.from_yaml(SHIPPED_CONFIG_PATH.read_text(encoding="utf-8"))
        container = WebsocketServerConfig.from_yaml(
            CONTAINER_CONFIG_PATH.read_text(encoding="utf-8")
        )
        self.assertEqual(shipped.server, container.server)
        assert shipped.sources[0].redis_config is not None
        assert container.sources[0].redis_config is not None
        self.assertEqual(container.sources[0].redis_config.host, "redis")
        self.assertEqual(
            shipped.sources[0].redis_config.channel_prefix,
            container.sources[0].redis_config.channel_prefix,
        )

    def test_reads_every_field(self) -> None:
        config = WebsocketServerConfig.from_yaml(COMPLETE_CONFIG)
        self.assertEqual(config.application, ApplicationConfig(name="test server", version="9.9.9"))
        self.assertEqual(config.server.host, "127.0.0.1")
        self.assertIs(config.server.log_level, LogLevel.WARNING)
        self.assertEqual(config.server.idle_timeout_seconds, IDLE_TIMEOUT)
        self.assertEqual(config.server.max_payload_bytes, MAX_PAYLOAD)
        self.assertEqual(
            [source.queue for source in config.sources], [QueueType.REDIS, QueueType.KAFKA]
        )


class LogLevelTest(unittest.TestCase):
    def test_every_level_maps_to_a_logging_number(self) -> None:
        for level in LogLevel:
            self.assertIsInstance(level.as_logging_level, int)
