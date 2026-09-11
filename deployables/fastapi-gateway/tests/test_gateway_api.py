import unittest

from fastapi_gateway.gateway_api import GatewayAPI
from fastapi_gateway.gateway_api_config import (
    ApplicationConfig,
    GatewayAPIConfig,
    GrpcConfig,
    ServerConfig,
)
from fastapi_gateway.gateway_clients import GatewayClients
from fastapi_gateway.log_level import LogLevel

CONFIGURED_PORT = 9091
UPSTREAM_PORT = 50051
MESSAGE_LIMIT = 4194304
A_LOBBY_PATH = "/internal/platform/lobby/read/table"
A_GAME_PATH = "/internal/platform/game/apply/command"
A_CATALOGUE_PATH = "/internal/platform/game/list/game_spec"


def application_config(root_path: str = "/api") -> ApplicationConfig:
    return ApplicationConfig(title="test gateway", version="9.9.9", root_path=root_path)


def config_for() -> GatewayAPIConfig:
    return GatewayAPIConfig(
        application=application_config(),
        server=ServerConfig(
            host="127.0.0.1",
            port=CONFIGURED_PORT,
            log_level=LogLevel.WARNING,
            access_log=False,
            proxy_headers=True,
            forwarded_allow_ips="10.0.0.1",
        ),
        grpc=GrpcConfig(
            hostname="127.0.0.1",
            port=UPSTREAM_PORT,
            max_receive_message_bytes=MESSAGE_LIMIT,
            max_send_message_bytes=MESSAGE_LIMIT,
        ),
    )


class BringupTest(unittest.TestCase):
    """
    Constructing a gateway reads the configuration. No client is opened and no
    socket is bound until `start` is called.
    """

    def test_a_gateway_is_built_without_touching_the_network(self) -> None:
        self.assertIsInstance(GatewayAPI(config=config_for()), GatewayAPI)

    def test_the_application_is_named_by_the_configuration(self) -> None:
        application = GatewayAPI.build_application(
            application_config(), GatewayClients.unconnected()
        )
        self.assertEqual(application.title, "test gateway")
        self.assertEqual(application.version, "9.9.9")
        self.assertEqual(application.root_path, "/api")

    def test_the_application_serves_the_routers_a_domain_publishes(self) -> None:
        """
        The document is what the application publishes. An included router is
        held unexpanded in `routes` until a request is matched against it.
        """
        application = GatewayAPI.build_application(
            application_config(), GatewayClients.unconnected()
        )
        paths = application.openapi()["paths"]
        self.assertIn(A_LOBBY_PATH, paths)
        self.assertIn(A_GAME_PATH, paths)
        self.assertIn(A_CATALOGUE_PATH, paths)


class GrpcAddressTest(unittest.TestCase):
    def test_the_address_is_the_hostname_and_port(self) -> None:
        self.assertEqual(config_for().grpc.address, f"127.0.0.1:{UPSTREAM_PORT}")
