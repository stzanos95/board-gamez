"""
Building the rules clients the configuration asked for.

Adding a game is a field on RulesConfig and one entry in the mapping here.
Nothing existing changes.
"""

from idl.game.model.game_type_pb2 import GameType

from game.service.grpc_rules_client import GrpcRulesClient
from game.service.rules_client_registry import RulesClientRegistry, RulesClientsByGameType
from game.service.rules_config import RulesConfig, RulesUpstreamsByGameType


class RulesClientProvider:
    """
    The one place rules clients are constructed.

    Holds which section of the configuration belongs to which game, so a game
    type is named beside its settings exactly once.
    """

    def __init__(self, config: RulesConfig) -> None:
        self._upstreams_by_game_type: RulesUpstreamsByGameType = {
            GameType.GAME_TYPE_CHESS: config.chess,
        }

    def get_rules_client_registry(self) -> RulesClientRegistry:
        """
        A client for every game the configuration names an upstream for.

        The clients come back unopened; the process opens them once its event
        loop is running.
        """
        clients: RulesClientsByGameType = {
            game_type: GrpcRulesClient(config=upstream)
            for game_type, upstream in self._upstreams_by_game_type.items()
            if upstream is not None
        }
        return RulesClientRegistry(clients)
