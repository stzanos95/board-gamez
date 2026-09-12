"""
What is done to a seat.

The one place the lobby decides who may sit where, and what giving a seat up
does. The rules every game shares are here: a seat is taken only while the
table waits for players, a player holds one seat at a time, a seat is taken
only as one of the choices its game offered, and a player who gives up a seat
in a game being played is withdrawn from that game first. Which choices a game
offers, and what a withdrawal does to it, is the game's.
"""

from game.controller.session_controller import SessionController
from idl.game.model.withdrawal_result_pb2 import WithdrawalOutcome
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

    def __init__(
        self, tables: TableController, seating: SeatingRegistry, sessions: SessionController
    ) -> None:
        self._tables = tables
        self._seating = seating
        self._sessions = sessions

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

    async def vacate_seat(self, table_id: str, player_id: str) -> SeatResult:
        """
        Give up the seat and stay at the table, and say how it went.

        A player in a game being played at the table is withdrawn from it
        before the seat is written, so the game never waits on someone who has
        gone. A withdrawal that cannot be written leaves the seat as it is.
        """
        table = await self._tables.read_table(table_id)
        if table is None:
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_TABLE_NOT_FOUND)
        if not SeatController._is_seated(table, player_id):
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_NOT_SEATED, table=table)
        if not await self._is_withdrawn(table_id, player_id):
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_VERSION_MOVED, table=table)
        stored = await self._tables.upsert_table(
            SeatAdapters.table_to_table_with_seat_vacated(table, player_id)
        )
        if stored is None:
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_VERSION_MOVED, table=table)
        return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_VACATED, table=stored)

    async def leave_table(self, table_id: str, player_id: str) -> SeatResult:
        """
        Leave the table, giving up a seat on the way out, and say how it went.

        A seated player is withdrawn from the game being played, as when
        vacating a seat. A player who is at the table without a seat is not in
        any game and leaves at once.
        """
        table = await self._tables.read_table(table_id)
        if table is None:
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_TABLE_NOT_FOUND)
        if player_id not in table.player_ids:
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_NOT_AT_TABLE, table=table)
        if SeatController._is_seated(table, player_id) and not await self._is_withdrawn(
            table_id, player_id
        ):
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_VERSION_MOVED, table=table)
        stored = await self._tables.upsert_table(
            SeatAdapters.table_to_table_with_player_left(table, player_id)
        )
        if stored is None:
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_VERSION_MOVED, table=table)
        return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_LEFT, table=stored)

    async def _is_withdrawn(self, table_id: str, player_id: str) -> bool:
        """
        Whether the player is out of the game at this table: withdrawn now,
        already withdrawn, never in it, or there is no game. Only a withdrawal
        the game could not write answers False.
        """
        result = await self._sessions.withdraw_player(table_id, player_id)
        return result.outcome != WithdrawalOutcome.WITHDRAWAL_OUTCOME_VERSION_MOVED

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
