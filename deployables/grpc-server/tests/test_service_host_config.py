import unittest
from pathlib import Path

from core.queue.config import QueueType
from game.repository.config import SessionRepositoryType
from lobby.repository.config import TableRepositoryType

from grpc_server.log_level import LogLevel
from grpc_server.service_host_config import ApplicationConfig, ServiceHostConfig

SHIPPED_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "grpc_server.yaml"

SHIPPED_PORT = 50051

COMPLETE_CONFIG = """
application:
  name: test server
  version: "9.9.9"
server:
  host: "127.0.0.1"
  port: 50999
  log_level: warning
  maximum_concurrent_rpcs: 8
  max_receive_message_bytes: 1024
  max_send_message_bytes: 2048
  graceful_shutdown_seconds: 3
  reflection: false
lobby:
  table_repository:
    repository: redis
    redis_config:
      host: "127.0.0.1"
      port: 6379
      database: 0
      key_prefix: "board-gamez-test"
game:
  session_repository:
    repository: redis
    redis_config:
      host: "127.0.0.1"
      port: 6379
      database: 0
      key_prefix: "board-gamez-test"
  deadlines:
    poll_interval_seconds: 0.5
queue:
  queue: redis
  redis_config:
    host: "127.0.0.1"
    port: 6379
    database: 0
    channel_prefix: "gamez-test"
"""


class ReadingSettingsTest(unittest.TestCase):
    def test_the_shipped_configuration_parses(self) -> None:
        config = ServiceHostConfig.from_yaml(SHIPPED_CONFIG_PATH.read_text(encoding="utf-8"))
        self.assertEqual(config.server.port, SHIPPED_PORT)
        self.assertIs(config.server.log_level, LogLevel.INFO)
        self.assertTrue(config.server.reflection)
        self.assertIs(config.lobby.table_repository.repository, TableRepositoryType.REDIS)
        self.assertIsNotNone(config.lobby.table_repository.redis_config)
        self.assertIs(config.game.session_repository.repository, SessionRepositoryType.REDIS)
        self.assertIs(config.queue.queue, QueueType.REDIS)

    def test_reads_every_field(self) -> None:
        config = ServiceHostConfig.from_yaml(COMPLETE_CONFIG)
        self.assertEqual(config.application, ApplicationConfig(name="test server", version="9.9.9"))
        self.assertEqual(config.server.host, "127.0.0.1")
        self.assertIs(config.server.log_level, LogLevel.WARNING)
        self.assertEqual(config.server.maximum_concurrent_rpcs, 8)
        self.assertEqual(config.server.graceful_shutdown_seconds, 3)
        self.assertFalse(config.server.reflection)
        self.assertIs(config.lobby.table_repository.repository, TableRepositoryType.REDIS)


class LogLevelTest(unittest.TestCase):
    def test_every_level_maps_to_a_logging_number(self) -> None:
        for level in LogLevel:
            self.assertIsInstance(level.as_logging_level, int)
