"""
What is done to a player's place at a table.

The one place the lobby decides how a table is opened and come to, who may sit
where, and what giving a seat up does. The rules every game shares are here: a
table is opened for a hosted game with a seat count the game allows, a table
that is finished or abandoned takes nobody, a seat is taken only while the
table waits for players, a player holds one seat at a time, a seat is taken
only as one of the choices its game offered, and a player who gives up a seat
in a game being played is withdrawn from that game first. Which choices a game
offers, how many seats it takes, and what a withdrawal does to it, is the
game's.
"""

import uuid

from core.queue.base_queue_publisher import BaseQueuePublisher
from core.queue.message_utils import QueueMessageUtils
from game.controller.rules_registry import RulesRegistry
from game.controller.session_controller import SessionController
from google.protobuf.message import Message
from idl.game.model.game_type_pb2 import GameType
from idl.game.model.withdrawal_result_pb2 import WithdrawalOutcome
from idl.lobby.model.seat_pb2 import SeatChoice, SeatChoiceCollection, SeatStatus
from idl.lobby.model.seat_result_pb2 import SeatOutcome, SeatResult
from idl.lobby.model.table_pb2 import Table, TableStatus

from lobby.adapters.event_adapters import EventAdapters
from lobby.adapters.seat_adapters import SeatAdapters
from lobby.controller.channel_names import LOBBY_CHANNEL, LobbyChannelNames
from lobby.controller.seating_registry import SeatingRegistry
from lobby.controller.table_controller import TableController

NO_CHOICES: tuple[SeatChoice, ...] = ()
NO_SEAT_NUMBER = 0
# The statuses under which a table takes players.
ACCEPTING_STATUSES = (TableStatus.TABLE_STATUS_WAITING, TableStatus.TABLE_STATUS_IN_PROGRESS)


class SeatController:
    """
    Every operation a seat has, and the collaborators they need.

    Takes and answers with the domain's own types. Nothing from `idl.lobby.dto`
    reaches this far.

    Every write that is stored is published as one event, on the table's
    channel and on the lobby's, after the write and never for a refused one.
    A withdrawal from the game is published by the session controller before
    the seat event follows it.

    Built once at the entry point and passed to whatever serves it.
    """

    def __init__(
        self,
        tables: TableController,
        seating: SeatingRegistry,
        sessions: SessionController,
        rules: RulesRegistry,
        queue_publisher: BaseQueuePublisher,
    ) -> None:
        self._tables = tables
        self._seating = seating
        self._sessions = sessions
        self._rules = rules
        self._queue_publisher = queue_publisher

    async def create_table(
        self, game_type: GameType, seat_count: int, player_id: str
    ) -> SeatResult:
        """
        Open a table for this game with this many seats, the opener at it and
        every seat empty, and say how it went.

        The id is minted here. The game must be one this process hosts, and
        the seat count must lie within the bounds its rules answer.
        """
        if game_type not in self._rules.get_game_types():
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_GAME_NOT_HOSTED)
        bounds = await self._rules.get_rules(game_type).read_bounds()
        if not bounds.minimum <= seat_count <= bounds.maximum:
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_SEAT_COUNT_NOT_ALLOWED)
        stored = await self._tables.upsert_table(
            SeatAdapters.creation_to_table(str(uuid.uuid4()), game_type, seat_count, player_id)
        )
        if stored is None:
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_VERSION_MOVED)
        await self._publish(stored, EventAdapters.table_to_table_created(stored, player_id))
        return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_CREATED, table=stored)

    async def join_table(self, table_id: str, player_id: str) -> SeatResult:
        """
        Come to the table without taking a seat, and say how it went.

        A finished or abandoned table takes nobody. A player already at the
        table is answered the table as it stands.
        """
        table = await self._tables.read_table(table_id)
        if table is None:
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_TABLE_NOT_FOUND)
        if table.status not in ACCEPTING_STATUSES:
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_NOT_ACCEPTING_PLAYERS, table=table)
        if player_id in table.player_ids:
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_ALREADY_AT_TABLE, table=table)
        stored = await self._tables.upsert_table(
            SeatAdapters.table_to_table_with_player_joined(table, player_id)
        )
        if stored is None:
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_VERSION_MOVED, table=table)
        await self._publish(stored, EventAdapters.table_to_player_joined(stored, player_id))
        return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_JOINED, table=stored)

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
        await self._publish(stored, EventAdapters.table_to_seat_taken(stored, player_id, choice))
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
        seat_number = SeatController._get_seat_number(table, player_id)
        stored = await self._tables.upsert_table(
            SeatAdapters.table_to_table_with_seat_vacated(table, player_id)
        )
        if stored is None:
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_VERSION_MOVED, table=table)
        await self._publish(
            stored, EventAdapters.table_to_seat_vacated(stored, player_id, seat_number)
        )
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
        seat_number = SeatController._get_seat_number(table, player_id)
        stored = await self._tables.upsert_table(
            SeatAdapters.table_to_table_with_player_left(table, player_id)
        )
        if stored is None:
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_VERSION_MOVED, table=table)
        await self._publish(
            stored, EventAdapters.table_to_player_left(stored, player_id, seat_number)
        )
        return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_LEFT, table=stored)

    async def _publish(self, table: Table, event: Message) -> None:
        """
        Send this event on the table's channel and on the lobby's.
        """
        envelope = QueueMessageUtils.pack(event)
        await self._queue_publisher.publish(LobbyChannelNames.get_table_channel(table.id), envelope)
        await self._queue_publisher.publish(LOBBY_CHANNEL, envelope)

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
    def _get_seat_number(table: Table, player_id: str) -> int:
        """
        The seat this player holds, or 0 when they hold none.
        """
        for seat in table.seats:
            if seat.status == SeatStatus.SEAT_STATUS_OCCUPIED and seat.player_id == player_id:
                return seat.number
        return NO_SEAT_NUMBER

    @staticmethod
    def _is_seated(table: Table, player_id: str) -> bool:
        return any(
            seat.status == SeatStatus.SEAT_STATUS_OCCUPIED and seat.player_id == player_id
            for seat in table.seats
        )
