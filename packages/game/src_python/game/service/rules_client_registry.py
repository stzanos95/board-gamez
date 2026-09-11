"""
The rules of every hosted game, found by game type.
"""

from idl.game.model.game_type_pb2 import GameType

from game.service.base_rules_client import BaseRulesClient

RulesClientsByGameType = dict[GameType, BaseRulesClient]


class RulesClientRegistry:
    """
    One rules client per game this process can host.

    A session names its game by type, and this is where that type becomes the
    rules to ask. A type with no client is a bringup error: nothing at run time
    can supply one.
    """

    def __init__(self, clients: RulesClientsByGameType) -> None:
        self._clients = dict(clients)

    def get_client(self, game_type: GameType) -> BaseRulesClient:
        """
        The rules that play this game.

        Raises RuntimeError when no rules were configured for it.
        """
        client = self._clients.get(game_type)
        if client is None:
            raise RuntimeError(
                f"no rules are configured for {GameType.Name(game_type)}; "
                f"configured games are "
                f"{', '.join(sorted(GameType.Name(known) for known in self._clients))}"
            )
        return client

    def get_game_types(self) -> tuple[GameType, ...]:
        """
        Every game this process has rules for.
        """
        return tuple(self._clients)

    async def open_all(self) -> None:
        for client in self._clients.values():
            await client.open()

    async def close_all(self) -> None:
        for client in self._clients.values():
            await client.close()
