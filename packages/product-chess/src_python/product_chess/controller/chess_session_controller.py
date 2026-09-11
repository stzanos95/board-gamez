"""
What is done to a game of chess being played at a table.

The one place chess decides anything about a table: which seats become which
participants, who may start a game, and how the platform's answer is shown to a
chess player. Which side a seat plays is ChessSeating's, whether a seat may be
taken is the lobby's, and whether an action is legal is the platform's and the
rules'.
"""

from game.controller.session_controller import SessionController
from idl.chess.model.action_pb2 import ChessAction
from idl.chess.model.session_pb2 import ActionResult, ChessSession
from idl.chess.model.table_pb2 import (
    ChessSeatChoice,
    ChessSeatChoiceCollection,
    ChessSeatResult,
    ChessTable,
)
from idl.game.model.game_type_pb2 import GameType
from idl.game.model.participant_pb2 import Participant
from lobby.controller.seat_controller import SeatController
from lobby.controller.table_controller import TableController

from product_chess.adapters.chess_seat_adapters import ChessSeatAdapters
from product_chess.adapters.chess_session_adapters import ChessSessionAdapters
from product_chess.controller.chess_rules import CHESS_PARTICIPANT_COUNT


class ChessSessionController:
    """
    Every operation a game of chess at a table has, and the collaborators they
    need.

    Takes and answers with chess's own types. Nothing from `idl.chess.dto`
    reaches this far.

    Built once at the entry point and passed to whatever serves it.
    """

    def __init__(
        self, tables: TableController, seats: SeatController, sessions: SessionController
    ) -> None:
        self._tables = tables
        self._seats = seats
        self._sessions = sessions

    async def read_table(self, table_id: str) -> ChessTable | None:
        """
        The table with every seat's side opened, or None when no chess table has
        that id.
        """
        table = await self._tables.read_table(table_id)
        if table is None or table.game_type != GameType.GAME_TYPE_CHESS:
            return None
        return ChessSeatAdapters.table_to_chess_table(table)

    async def list_seat_choices(self, table_id: str, player_id: str) -> ChessSeatChoiceCollection:
        """
        Every seat this player may take at this table now, with the side each
        plays.
        """
        return ChessSeatAdapters.seat_choice_collection_to_chess_seat_choice_collection(
            await self._seats.list_seat_choices(table_id, player_id)
        )

    async def take_seat(
        self, table_id: str, player_id: str, choice: ChessSeatChoice, expected_version: int
    ) -> ChessSeatResult:
        """
        Seat this player as the choice says, and say how it went.
        """
        result = await self._seats.take_seat(
            table_id,
            player_id,
            ChessSeatAdapters.chess_seat_choice_to_seat_choice(choice),
            expected_version,
        )
        return ChessSeatAdapters.seat_result_to_chess_seat_result(result)

    async def start_game(self, table_id: str, player_id: str) -> ChessSession | None:
        """
        Start the game at this table and answer it as the caller may see it.

        The caller must hold one of the table's seats, and every seat must be
        taken. A table already playing a game is answered that game. None comes
        back when the table is not a chess table, is not full, or the caller is
        not seated at it.
        """
        table = await self._tables.read_table(table_id)
        if table is None or table.game_type != GameType.GAME_TYPE_CHESS:
            return None
        participants = ChessSessionAdapters.table_to_participants(table)
        if len(participants) != CHESS_PARTICIPANT_COUNT:
            return None
        if not ChessSessionController._is_seated(participants, player_id):
            return None
        view = await self._sessions.create_session(
            table_id, GameType.GAME_TYPE_CHESS, participants, player_id
        )
        if view is None:
            return None
        return ChessSessionAdapters.session_view_to_chess_session(view)

    async def read_game(self, table_id: str, player_id: str) -> ChessSession | None:
        """
        The game at this table as the caller may see it, or None when there is
        none.
        """
        view = await self._sessions.read_session(table_id, player_id)
        if view is None:
            return None
        return ChessSessionAdapters.session_view_to_chess_session(view)

    async def play_action(
        self,
        table_id: str,
        player_id: str,
        command_id: str,
        action: ChessAction,
        expected_version: int,
    ) -> ActionResult:
        """
        Do one thing in the game at this table, and say how it went.
        """
        result = await self._sessions.apply_command(
            table_id,
            player_id,
            command_id,
            ChessSessionAdapters.chess_action_to_payload(action),
            expected_version,
        )
        return ChessSessionAdapters.command_result_to_action_result(result)

    @staticmethod
    def _is_seated(participants: tuple[Participant, ...], player_id: str) -> bool:
        return any(participant.player_id == player_id for participant in participants)
