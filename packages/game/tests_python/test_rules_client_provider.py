import unittest

from idl.game.model.game_type_pb2 import GameType

from game.service.rules_client_provider import RulesClientProvider
from game.service.rules_config import RulesConfig, RulesUpstreamConfig

CHESS_UPSTREAM = RulesUpstreamConfig(
    hostname="product-chess",
    port=50052,
    max_receive_message_bytes=4194304,
    max_send_message_bytes=4194304,
)


class RulesClientProviderTest(unittest.TestCase):
    def test_a_game_with_an_upstream_gets_a_client(self) -> None:
        provider = RulesClientProvider(RulesConfig(chess=CHESS_UPSTREAM))

        registry = provider.get_rules_client_registry()

        self.assertEqual(registry.get_game_types(), (GameType.GAME_TYPE_CHESS,))
        self.assertIsNotNone(registry.get_client(GameType.GAME_TYPE_CHESS))

    def test_a_game_without_an_upstream_is_not_served(self) -> None:
        registry = RulesClientProvider(RulesConfig()).get_rules_client_registry()

        self.assertEqual(registry.get_game_types(), ())
        with self.assertRaises(RuntimeError):
            registry.get_client(GameType.GAME_TYPE_CHESS)

    def test_the_address_is_the_hostname_and_port(self) -> None:
        self.assertEqual(CHESS_UPSTREAM.address, "product-chess:50052")
