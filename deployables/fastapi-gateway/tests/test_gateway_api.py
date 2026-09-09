import unittest

from fastapi_gateway.gateway_api import GatewayAPI
from fastapi_gateway.gateway_api_config import ApplicationConfig, GatewayAPIConfig, ServerConfig
from fastapi_gateway.log_level import LogLevel

CONFIGURED_PORT = 9091


def config_for(root_path: str = "/api") -> GatewayAPIConfig:
    return GatewayAPIConfig(
        application=ApplicationConfig(title="test gateway", version="9.9.9", root_path=root_path),
        server=ServerConfig(
            host="127.0.0.1",
            port=CONFIGURED_PORT,
            log_level=LogLevel.WARNING,
            access_log=False,
            proxy_headers=True,
            forwarded_allow_ips="10.0.0.1",
        ),
    )


class BringupTest(unittest.TestCase):
    """
    Bringup builds the application and the server around it. Nothing binds a
    socket until `start` is called.
    """

    def test_the_application_is_named_by_the_configuration(self) -> None:
        gateway = GatewayAPI(config=config_for())
        self.assertEqual(gateway.application.title, "test gateway")
        self.assertEqual(gateway.application.version, "9.9.9")
        self.assertEqual(gateway.application.root_path, "/api")
