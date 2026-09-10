import unittest
from pathlib import Path

from fastapi_gateway.gateway_api_config import ApplicationConfig, GatewayAPIConfig
from fastapi_gateway.log_level import LogLevel

SHIPPED_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "fastapi_gateway.yaml"

COMPLETE_CONFIG = """
application:
  title: test gateway
  version: "9.9.9"
  root_path: "/api"
server:
  host: "127.0.0.1"
  port: 9090
  log_level: warning
  access_log: false
  proxy_headers: true
  forwarded_allow_ips: "10.0.0.1"
upstreams:
  lobby:
    hostname: "127.0.0.1"
    port: 50051
    max_receive_message_bytes: 1024
    max_send_message_bytes: 2048
"""


class ReadingSettingsTest(unittest.TestCase):
    def test_the_shipped_configuration_parses(self) -> None:
        config = GatewayAPIConfig.from_yaml(SHIPPED_CONFIG_PATH.read_text(encoding="utf-8"))
        self.assertEqual(config.server.port, 8080)
        self.assertIs(config.server.log_level, LogLevel.INFO)
        self.assertTrue(config.server.proxy_headers)

    def test_reads_every_field(self) -> None:
        config = GatewayAPIConfig.from_yaml(COMPLETE_CONFIG)
        self.assertEqual(
            config.application,
            ApplicationConfig(title="test gateway", version="9.9.9", root_path="/api"),
        )
        self.assertEqual(config.server.host, "127.0.0.1")
        self.assertEqual(config.server.port, 9090)
        self.assertIs(config.server.log_level, LogLevel.WARNING)
        self.assertFalse(config.server.access_log)
        self.assertEqual(config.server.forwarded_allow_ips, "10.0.0.1")
        self.assertEqual(config.upstreams.lobby.address, "127.0.0.1:50051")
        self.assertEqual(config.upstreams.lobby.max_receive_message_bytes, 1024)
