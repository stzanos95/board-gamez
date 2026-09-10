import unittest

from fastapi.routing import APIRoute
from lobby.service.grpc_table_client import GrpcTableClient

from fastapi_gateway.gateway_api import GatewayAPI
from fastapi_gateway.gateway_api_config import (
    ApplicationConfig,
    GatewayAPIConfig,
    GrpcConfig,
    ServerConfig,
    UpstreamsConfig,
)
from fastapi_gateway.log_level import LogLevel

CONFIGURED_PORT = 9091
UPSTREAM_PORT = 50051
MESSAGE_LIMIT = 4194304
A_LOBBY_PATH = "/internal/platform/lobby/read/table"


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
        upstreams=UpstreamsConfig(
            lobby=GrpcConfig(
                hostname="127.0.0.1",
                port=UPSTREAM_PORT,
                max_receive_message_bytes=MESSAGE_LIMIT,
                max_send_message_bytes=MESSAGE_LIMIT,
            )
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
        application = GatewayAPI.build_application(application_config(), GrpcTableClient())
        self.assertEqual(application.title, "test gateway")
        self.assertEqual(application.version, "9.9.9")
        self.assertEqual(application.root_path, "/api")

    def test_the_application_serves_the_routers_a_domain_publishes(self) -> None:
        application = GatewayAPI.build_application(application_config(), GrpcTableClient())
        paths = {route.path for route in application.routes if isinstance(route, APIRoute)}
        self.assertIn(A_LOBBY_PATH, paths)


class UpstreamTest(unittest.TestCase):
    def test_an_upstream_address_is_its_hostname_and_port(self) -> None:
        self.assertEqual(config_for().upstreams.lobby.address, f"127.0.0.1:{UPSTREAM_PORT}")
