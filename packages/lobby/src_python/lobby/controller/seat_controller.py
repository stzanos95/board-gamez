"""
What is done to a seat.

The one place the lobby decides who may sit where. The rules every game shares
are here: a seat is taken only while the table waits for players, a player holds
one seat at a time, and a seat is taken only as one of the choices its game
offered. Which choices a game offers is the game's, reached through its seating.
"""

from idl.lobby.model.seat_pb2 import SeatChoice, SeatChoiceCollection, SeatStatus
from idl.lobby.model.seat_result_pb2 import SeatOutcome, SeatResult
from idl.lobby.model.table_pb2 import Table, TableStatus

from lobby.adapters.seat_adapters import SeatAdapters
from lobby.controller.seating_registry import SeatingRegistry
from lobby.controller.table_controller import TableController

NO_CHOICES: tuple[SeatChoice, ...] = ()


class SeatController:
    """
    Every operation a seat has, and the collaborators they need.

    Takes and answers with the domain's own types. Nothing from `idl.lobby.dto`
    reaches this far.

    Built once at the entry point and passed to whatever serves it.
    """

    def __init__(self, tables: TableController, seating: SeatingRegistry) -> None:
        self._tables = tables
        self._seating = seating

    async def list_seat_choices(self, table_id: str, player_id: str) -> SeatChoiceCollection:
        """
        Every seat this player may take at this table now.

        Empty when no table has that id, when the table is not waiting for
        players, when the player already holds a seat there, or when the game
        offers them none.
        """
        table = await self._tables.read_table(table_id)
        if table is None:
            return SeatAdapters.seat_choices_to_collection(NO_CHOICES)
        return SeatAdapters.seat_choices_to_collection(
            await self._get_seat_choices(table, player_id)
        )

    async def take_seat(
        self, table_id: str, player_id: str, choice: SeatChoice, expected_version: int
    ) -> SeatResult:
        """
        Seat this player as the choice says, and say how it went.

        The choice must be one the game offers this player at the table as it
        stands at `expected_version`. Taking a seat puts the player at the table
        if they were not already there.
        """
        table = await self._tables.read_table(table_id)
        if table is None:
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_TABLE_NOT_FOUND)
        if table.version != expected_version:
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_VERSION_MOVED, table=table)
        if choice not in await self._get_seat_choices(table, player_id):
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_NOT_OFFERED, table=table)
        stored = await self._tables.upsert_table(
            SeatAdapters.table_to_table_with_seat_taken(table, player_id, choice)
        )
        if stored is None:
            # Another writer moved the table between the read and the write.
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_VERSION_MOVED, table=table)
        return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_TAKEN, table=stored)

    async def _get_seat_choices(self, table: Table, player_id: str) -> tuple[SeatChoice, ...]:
        """
        What the game offers this player, once the lobby's own rules allow a
        seat to be taken at all.
        """
        if table.status != TableStatus.TABLE_STATUS_WAITING:
            return NO_CHOICES
        if SeatController._is_seated(table, player_id):
            return NO_CHOICES
        return await self._seating.get_seating(table.game_type).list_seat_choices(table, player_id)

    @staticmethod
    def _is_seated(table: Table, player_id: str) -> bool:
        return any(
            seat.status == SeatStatus.SEAT_STATUS_OCCUPIED and seat.player_id == player_id
            for seat in table.seats
        )
