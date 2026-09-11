"""
What a game answers about its seats, as the lobby asks it.
"""

from abc import ABC, abstractmethod

from idl.lobby.model.seat_pb2 import SeatChoice
from idl.lobby.model.table_pb2 import Table


class BaseSeating(ABC):
    """
    How one game seats its players, whichever game.

    Typed on the domain's models, so a controller holding one never sees a
    request. Every call carries the table it acts on; nothing is held between
    calls on either side, and no implementation writes a table.
    """

    @abstractmethod
    async def list_seat_choices(self, table: Table, player_id: str) -> tuple[SeatChoice, ...]:
        """
        Every seat this player may take at this table now, each paired with the
        role they would take it with.

        The table is waiting for players and the player holds no seat at it;
        both are settled before a game is asked. Which open seats are offered,
        and with which role, is the game's own decision.
        """
