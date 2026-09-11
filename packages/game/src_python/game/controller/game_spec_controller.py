"""
What games there are.
"""

from idl.game.model.game_spec_pb2 import GameSpec, GameSpecCollection

from game.service.rules_client_registry import RulesClientRegistry


class GameSpecController:
    """
    The catalogue of games this process hosts, assembled from what each game's
    rules answer about themselves.
    """

    def __init__(self, rules: RulesClientRegistry) -> None:
        self._rules = rules

    async def list_game_spec(self) -> GameSpecCollection:
        """
        Every hosted game and the participants it takes.
        """
        specs = []
        for game_type in self._rules.get_game_types():
            bounds = await self._rules.get_client(game_type).read_bounds()
            specs.append(GameSpec(game_type=game_type, bounds=bounds))
        return GameSpecCollection(game_spec_items=specs)
