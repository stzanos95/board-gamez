"""
The seating of every hosted game, found by game type.
"""

from idl.game.model.game_type_pb2 import GameType

from lobby.controller.base_seating import BaseSeating

SeatingByGameType = dict[GameType, BaseSeating]


class SeatingRegistry:
    """
    The seating of each game this process can host.

    A table names its game by type, and this is where that type becomes the
    seating to ask. A type with no seating is a bringup error: nothing at run
    time can supply it.
    """

    def __init__(self, seating: SeatingByGameType) -> None:
        self._seating = dict(seating)

    def get_seating(self, game_type: GameType) -> BaseSeating:
        """
        The seating that offers this game's seats.

        Raises RuntimeError when no seating was registered for it.
        """
        seating = self._seating.get(game_type)
        if seating is None:
            raise RuntimeError(
                f"no seating is registered for {GameType.Name(game_type)}; "
                f"registered games are "
                f"{', '.join(sorted(GameType.Name(known) for known in self._seating))}"
            )
        return seating
