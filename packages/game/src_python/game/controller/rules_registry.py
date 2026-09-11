"""
The rules of every hosted game, found by game type.
"""

from idl.game.model.game_type_pb2 import GameType

from game.controller.base_rules import BaseRules

RulesByGameType = dict[GameType, BaseRules]


class RulesRegistry:
    """
    The rules of each game this process can host.

    A session names its game by type, and this is where that type becomes the
    rules to ask. A type with no rules is a bringup error: nothing at run time
    can supply them.
    """

    def __init__(self, rules: RulesByGameType) -> None:
        self._rules = dict(rules)

    def get_rules(self, game_type: GameType) -> BaseRules:
        """
        The rules that play this game.

        Raises RuntimeError when no rules were registered for it.
        """
        rules = self._rules.get(game_type)
        if rules is None:
            raise RuntimeError(
                f"no rules are registered for {GameType.Name(game_type)}; "
                f"registered games are "
                f"{', '.join(sorted(GameType.Name(known) for known in self._rules))}"
            )
        return rules

    def get_game_types(self) -> tuple[GameType, ...]:
        """
        Every game this process has rules for.
        """
        return tuple(self._rules)
