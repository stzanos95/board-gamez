"""
What is done to a player's place at a table.

The one place the lobby decides how a table is opened and come to, who may sit
where, when the game at it begins and ends, and what giving a seat up does.
The rules every game shares are here: a table is opened for a hosted game with
a seat count the game allows, a table takes players only while it waits for
them and has a seat open, a seat is taken only while the table waits for
players, a player holds one seat at a time, a seat is taken only as one of the
choices its game offered, a game is started only at a table that waits and the
table is in progress from then on, a player who gives up a seat in a game
being played is withdrawn from that game first, the table is finished once its
game has a result, and the table is gone once its last player has left. Which
choices a game offers, how many seats it takes, which seats become which
participants, and what a withdrawal does to it, is the game's.
"""

import uuid

from core.queue.base_queue_publisher import BaseQueuePublisher
from core.queue.message_utils import QueueMessageUtils
from game.controller.rules_registry import RulesRegistry
from game.controller.session_controller import SessionController
from google.protobuf import any_pb2
from google.protobuf.message import Message
from idl.game.model.command_result_pb2 import CommandResult
from idl.game.model.game_type_pb2 import GameType
from idl.game.model.participant_pb2 import Participant
from idl.game.model.session_pb2 import SessionView
from idl.game.model.withdrawal_result_pb2 import WithdrawalOutcome, WithdrawalResult
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
NO_PLAYERS = 0
# How many times a table write that follows a game write is read and made
# again after losing to another writer.
TABLE_WRITE_ATTEMPTS = 3


class SeatController:
    """
    Every operation a seat has, and the collaborators they need.

    Takes and answers with the domain's own types. Nothing from `idl.lobby.dto`
    reaches this far.

    Every write that is stored is published as one event, on the table's
    channel and on the lobby's, after the write and never for a refused one.
    A withdrawal from the game is published by the session controller before
    the seat event follows it, and a command is published by the session
    controller before the table it finishes follows it.

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

        A table takes a player only while it waits for players and has a seat
        open. A player already at the table is answered the table as it
        stands.
        """
        table = await self._tables.read_table(table_id)
        if table is None:
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_TABLE_NOT_FOUND)
        if player_id in table.player_ids:
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_ALREADY_AT_TABLE, table=table)
        if table.status != TableStatus.TABLE_STATUS_WAITING:
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_NOT_ACCEPTING_PLAYERS, table=table)
        if SeatController._is_full(table):
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_TABLE_FULL, table=table)
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

    async def start_game(
        self, table_id: str, participants: tuple[Participant, ...], player_id: str
    ) -> SessionView | None:
        """
        Start the game at this table for these participants, put the table in
        progress, and answer the game as the caller may see it.

        A table already in progress is answered the game being played at it.
        None comes back when no table has that id, when the table is finished
        or abandoned, or when the game does not take these participants.

        The game is written before the table. A table write that loses to
        another writer is read and made again, up to TABLE_WRITE_ATTEMPTS times; a
        table found in progress on the way is another caller's start of the
        same game.
        """
        table = await self._tables.read_table(table_id)
        if table is None:
            return None
        if table.status == TableStatus.TABLE_STATUS_IN_PROGRESS:
            return await self._sessions.read_session(table_id, player_id)
        if table.status != TableStatus.TABLE_STATUS_WAITING:
            return None
        view = await self._sessions.create_session(
            table_id, table.game_type, participants, player_id
        )
        if view is None:
            return None
        attempts = 0
        while attempts < TABLE_WRITE_ATTEMPTS:
            attempts += 1
            stored = await self._tables.upsert_table(SeatAdapters.table_to_table_in_progress(table))
            if stored is not None:
                await self._publish(stored, EventAdapters.table_to_table_started(stored))
                return view
            table = await self._tables.read_table(table_id)
            if table is None:
                return None
            if table.status == TableStatus.TABLE_STATUS_IN_PROGRESS:
                return view
        return None

    async def apply_command(
        self,
        table_id: str,
        player_id: str,
        command_id: str,
        action: any_pb2.Any,
        expected_version: int,
    ) -> CommandResult:
        """
        Do one thing in the game at this table, and say how it went.

        The command is the session controller's to decide. When the game it
        answers with has a result, the table is finished.
        """
        result = await self._sessions.apply_command(
            table_id, player_id, command_id, action, expected_version
        )
        if result.HasField("session") and result.session.state.HasField("result"):
            await self._finish_table(table_id)
        return result

    async def vacate_seat(self, table_id: str, player_id: str) -> SeatResult:
        """
        Give up the seat and stay at the table, and say how it went.

        A player in a game being played at the table is withdrawn from it
        before the seat is written, so the game never waits on someone who has
        gone. A withdrawal that cannot be written leaves the seat as it is. A
        withdrawal that ends the game finishes the table.
        """
        table = await self._tables.read_table(table_id)
        if table is None:
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_TABLE_NOT_FOUND)
        if not SeatController._is_seated(table, player_id):
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_NOT_SEATED, table=table)
        withdrawal = await self._withdraw(table_id, player_id)
        if not SeatController._is_withdrawn(withdrawal):
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
        if SeatController._is_game_over(withdrawal):
            finished = await self._finish_table(table_id)
            if finished is not None:
                stored = finished
        return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_VACATED, table=stored)

    async def leave_table(self, table_id: str, player_id: str) -> SeatResult:
        """
        Leave the table, giving up a seat on the way out, and say how it went.

        A seated player is withdrawn from the game being played, as when
        vacating a seat, and a withdrawal that ends the game finishes the
        table. A player who is at the table without a seat is not in any game
        and leaves at once. The last player to leave takes the table with
        them: it is retired, and the table answered is the last it stood as.
        """
        table = await self._tables.read_table(table_id)
        if table is None:
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_TABLE_NOT_FOUND)
        if player_id not in table.player_ids:
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_NOT_AT_TABLE, table=table)
        withdrawal: WithdrawalResult | None = None
        if SeatController._is_seated(table, player_id):
            withdrawal = await self._withdraw(table_id, player_id)
            if not SeatController._is_withdrawn(withdrawal):
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
        if len(stored.player_ids) == NO_PLAYERS:
            await self._tables.delete_table(stored.id, stored.version)
            return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_LEFT, table=stored)
        if withdrawal is not None and SeatController._is_game_over(withdrawal):
            finished = await self._finish_table(table_id)
            if finished is not None:
                stored = finished
        return SeatResult(outcome=SeatOutcome.SEAT_OUTCOME_LEFT, table=stored)

    async def _publish(self, table: Table, event: Message) -> None:
        """
        Send this event on the table's channel and on the lobby's.
        """
        envelope = QueueMessageUtils.pack(event)
        await self._queue_publisher.publish(LobbyChannelNames.get_table_channel(table.id), envelope)
        await self._queue_publisher.publish(LOBBY_CHANNEL, envelope)

    async def _withdraw(self, table_id: str, player_id: str) -> WithdrawalResult:
        """
        Take the player out of the game at this table, and answer how it went.
        """
        return await self._sessions.withdraw_player(table_id, player_id)

    async def _finish_table(self, table_id: str) -> Table | None:
        """
        Put the table at rest once its game is over, and answer it as stored.

        A table write that loses to another writer is read and made again, up
        to TABLE_WRITE_ATTEMPTS times. None comes back when the table is gone,
        is not in progress, or could not be written; a table found finished on
        the way was finished by another caller, and is answered as it stands.
        """
        attempts = 0
        while attempts < TABLE_WRITE_ATTEMPTS:
            attempts += 1
            table = await self._tables.read_table(table_id)
            if table is None:
                return None
            if table.status == TableStatus.TABLE_STATUS_FINISHED:
                return table
            if table.status != TableStatus.TABLE_STATUS_IN_PROGRESS:
                return None
            stored = await self._tables.upsert_table(SeatAdapters.table_to_table_finished(table))
            if stored is not None:
                await self._publish(stored, EventAdapters.table_to_table_finished(stored))
                return stored
        return None

    @staticmethod
    def _is_withdrawn(withdrawal: WithdrawalResult) -> bool:
        """
        Whether the player is out of the game: withdrawn now, already
        withdrawn, never in it, or there is no game. Only a withdrawal the
        game could not write answers False.
        """
        return withdrawal.outcome != WithdrawalOutcome.WITHDRAWAL_OUTCOME_VERSION_MOVED

    @staticmethod
    def _is_game_over(withdrawal: WithdrawalResult) -> bool:
        """
        Whether the game the withdrawal answered with has a result.
        """
        return withdrawal.HasField("session") and withdrawal.session.state.HasField("result")

    @staticmethod
    def _is_full(table: Table) -> bool:
        return all(seat.status == SeatStatus.SEAT_STATUS_OCCUPIED for seat in table.seats)

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
