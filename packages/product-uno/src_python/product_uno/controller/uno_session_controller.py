"""
What is done to a game of UNO being played at a table.

The one place UNO decides anything about a table: which seats become which
participants, who may start a game, and how the platform's answer is shown to
a UNO player. Whether a seat may be taken is the lobby's, and whether an
action is legal is the platform's and the rules'.
"""

from game.controller.session_controller import SessionController
from idl.game.model.game_type_pb2 import GameType
from idl.game.model.participant_pb2 import Participant
from idl.uno.model.action_pb2 import UnoAction
from idl.uno.model.session_pb2 import ActionResult, UnoSession
from idl.uno.model.table_pb2 import (
    UnoSeatChoice,
    UnoSeatChoiceCollection,
    UnoSeatResult,
    UnoTable,
)
from lobby.controller.seat_controller import SeatController
from lobby.controller.table_controller import TableController

from product_uno.adapters.uno_seat_adapters import UnoSeatAdapters
from product_uno.adapters.uno_session_adapters import UnoSessionAdapters


class UnoSessionController:
    """
    Every operation a game of UNO at a table has, and the collaborators they
    need.

    Takes and answers with UNO's own types. Nothing from `idl.uno.dto` reaches
    this far.

    Built once at the entry point and passed to whatever serves it.
    """

    def __init__(
        self, tables: TableController, seats: SeatController, sessions: SessionController
    ) -> None:
        self._tables = tables
        self._seats = seats
        self._sessions = sessions

    async def read_table(self, table_id: str) -> UnoTable | None:
        """
        The table as UNO sees it, or None when no UNO table has that id.
        """
        table = await self._tables.read_table(table_id)
        if table is None or table.game_type != GameType.GAME_TYPE_UNO:
            return None
        return UnoSeatAdapters.table_to_uno_table(table)

    async def list_seat_choices(self, table_id: str, player_id: str) -> UnoSeatChoiceCollection:
        """
        Every seat this player may take at this table now.
        """
        return UnoSeatAdapters.seat_choice_collection_to_uno_seat_choice_collection(
            await self._seats.list_seat_choices(table_id, player_id)
        )

    async def take_seat(
        self, table_id: str, player_id: str, choice: UnoSeatChoice, expected_version: int
    ) -> UnoSeatResult:
        """
        Seat this player as the choice says, and say how it went.
        """
        result = await self._seats.take_seat(
            table_id,
            player_id,
            UnoSeatAdapters.uno_seat_choice_to_seat_choice(choice),
            expected_version,
        )
        return UnoSeatAdapters.seat_result_to_uno_seat_result(result)

    async def start_game(self, table_id: str, player_id: str) -> UnoSession | None:
        """
        Start the game at this table and answer it as the caller may see it.

        The caller must hold one of the table's seats, and every seat must be
        taken. A table already playing a game is answered that game. None comes
        back when the table is not a UNO table, is not full, is not waiting for
        players, or the caller is not seated at it.
        """
        table = await self._tables.read_table(table_id)
        if table is None or table.game_type != GameType.GAME_TYPE_UNO:
            return None
        participants = UnoSessionAdapters.table_to_participants(table)
        if len(participants) != len(table.seats):
            return None
        if not UnoSessionController._is_seated(participants, player_id):
            return None
        view = await self._seats.start_game(table_id, participants, player_id)
        if view is None:
            return None
        return UnoSessionAdapters.session_view_to_uno_session(view)

    async def read_game(self, table_id: str, player_id: str) -> UnoSession | None:
        """
        The game at this table as the caller may see it, or None when there is
        none.
        """
        view = await self._sessions.read_session(table_id, player_id)
        if view is None:
            return None
        return UnoSessionAdapters.session_view_to_uno_session(view)

    async def play_action(
        self,
        table_id: str,
        player_id: str,
        command_id: str,
        action: UnoAction,
        expected_version: int,
    ) -> ActionResult:
        """
        Do one thing in the game at this table, and say how it went.
        """
        result = await self._sessions.apply_command(
            table_id,
            player_id,
            command_id,
            UnoSessionAdapters.uno_action_to_payload(action),
            expected_version,
        )
        return UnoSessionAdapters.command_result_to_action_result(result)

    @staticmethod
    def _is_seated(participants: tuple[Participant, ...], player_id: str) -> bool:
        return any(participant.player_id == player_id for participant in participants)
