import unittest

from core.protobuf.message_utils import ProtobufMessageUtils
from idl.game.dto import command_pb2
from idl_fastapi.google.protobuf import Any
from idl_fastapi.idl.game.dto import ApplyCommandRequest

from fastapi_gateway.gateway_api import GatewayAPI
from fastapi_gateway.gateway_api_config import (
    ApplicationConfig,
    GatewayAPIConfig,
    GrpcConfig,
    ServerConfig,
)
from fastapi_gateway.gateway_clients import GatewayClients
from fastapi_gateway.log_level import LogLevel
from fastapi_gateway.payload_types import PayloadTypeRegistry
from fastapi_gateway.products.gateway_products import GatewayProducts

CONFIGURED_PORT = 9091
UPSTREAM_PORT = 50051
MESSAGE_LIMIT = 4194304
A_LOBBY_PATH = "/internal/platform/lobby/read/table"
A_GAME_PATH = "/internal/platform/game/apply/command"
A_CATALOGUE_PATH = "/internal/platform/game/list/game_spec"
A_CHESS_PATH = "/internal/product/chess/play/action"
A_UNO_PATH = "/internal/product/uno/play/action"


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
            application_config(), GatewayClients.unconnected(GatewayProducts.build())
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
            application_config(), GatewayClients.unconnected(GatewayProducts.build())
        )
        paths = application.openapi()["paths"]
        self.assertIn(A_LOBBY_PATH, paths)
        self.assertIn(A_GAME_PATH, paths)
        self.assertIn(A_CATALOGUE_PATH, paths)
        self.assertIn(A_CHESS_PATH, paths)
        self.assertIn(A_UNO_PATH, paths)


class GrpcAddressTest(unittest.TestCase):
    def test_the_address_is_the_hostname_and_port(self) -> None:
        self.assertEqual(config_for().grpc.address, f"127.0.0.1:{UPSTREAM_PORT}")


class PayloadTypeTest(unittest.TestCase):
    def test_a_chess_action_can_be_read_from_json(self) -> None:
        """
        Resolving an `@type` needs the type's module imported, which is what
        the registry is for.
        """
        self.assertIn(
            "idl.chess.model.ChessAction",
            PayloadTypeRegistry.get_type_names(GatewayProducts.build()),
        )
        request = ProtobufMessageUtils.message_from_pydantic_model(
            ApplyCommandRequest(
                sessionId="t-1",
                commandId="c-1",
                playerId="p-1",
                action=Any.model_validate(
                    {
                        "@type": "type.googleapis.com/idl.chess.model.ChessAction",
                        "resignation": {},
                    }
                ),
                expectedVersion="1",
            ),
            command_pb2.ApplyCommandRequest,
        )
        self.assertEqual(request.action.type_url, "type.googleapis.com/idl.chess.model.ChessAction")

    def test_a_uno_action_can_be_read_from_json(self) -> None:
        self.assertIn(
            "idl.uno.model.UnoAction",
            PayloadTypeRegistry.get_type_names(GatewayProducts.build()),
        )
        request = ProtobufMessageUtils.message_from_pydantic_model(
            ApplyCommandRequest(
                sessionId="t-1",
                commandId="c-1",
                playerId="p-1",
                action=Any.model_validate(
                    {
                        "@type": "type.googleapis.com/idl.uno.model.UnoAction",
                        "draw": {},
                    }
                ),
                expectedVersion="1",
            ),
            command_pb2.ApplyCommandRequest,
        )
        self.assertEqual(request.action.type_url, "type.googleapis.com/idl.uno.model.UnoAction")
