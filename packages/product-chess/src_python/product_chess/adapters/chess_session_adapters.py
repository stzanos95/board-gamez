"""
A game of chess being played, between the shapes it takes.

A request carries what an operation needs; a controller takes those arguments and
answers with chess's own types. Turning one into the other is what a servicer
delegates here, so no layer above the controller reads a field off a request.

A contract also produces two families of type — protobuf messages for gRPC and
pydantic models for HTTP — and a caller crossing between them converts here too.

The platform answers a session with its game packed opaquely and the viewer
named by participant number. Opening the game and naming the viewer's colour is
the projection into a ChessSession, and it runs here.
"""

from core.protobuf.message_utils import ProtobufMessageUtils
from google.protobuf import any_pb2
from idl.chess.dto import game_pb2 as chess_game_dto_pb2
from idl.chess.model import game_pb2, piece_pb2
from idl.chess.model.action_pb2 import ChessAction
from idl.chess.model.session_pb2 import ActionResult, ChessSession
from idl.game.model.command_result_pb2 import CommandResult
from idl.game.model.participant_pb2 import Participant
from idl.game.model.session_pb2 import SessionView
from idl.lobby.model.seat_pb2 import SeatStatus
from idl.lobby.model.table_pb2 import Table
from idl_fastapi.idl.chess.dto import (
    PlayActionRequest,
    PlayActionResponse,
    ReadGameRequest,
    ReadGameResponse,
    StartGameRequest,
    StartGameResponse,
)


class ChessSessionAdapters:
    """
    Every ChessService message and every platform type, converted to what the
    layer beneath it takes.
    """

    # --- a request, to the arguments an operation takes ----------------------

    @staticmethod
    def start_request_to_table_id(request: chess_game_dto_pb2.StartGameRequest) -> str:
        return request.table_id

    @staticmethod
    def start_request_to_player_id(request: chess_game_dto_pb2.StartGameRequest) -> str:
        return request.player_id

    @staticmethod
    def read_request_to_table_id(request: chess_game_dto_pb2.ReadGameRequest) -> str:
        return request.table_id

    @staticmethod
    def read_request_to_player_id(request: chess_game_dto_pb2.ReadGameRequest) -> str:
        return request.player_id

    @staticmethod
    def play_request_to_table_id(request: chess_game_dto_pb2.PlayActionRequest) -> str:
        return request.table_id

    @staticmethod
    def play_request_to_player_id(request: chess_game_dto_pb2.PlayActionRequest) -> str:
        return request.player_id

    @staticmethod
    def play_request_to_command_id(request: chess_game_dto_pb2.PlayActionRequest) -> str:
        return request.command_id

    @staticmethod
    def play_request_to_action(request: chess_game_dto_pb2.PlayActionRequest) -> ChessAction:
        return request.action

    @staticmethod
    def play_request_to_expected_version(request: chess_game_dto_pb2.PlayActionRequest) -> int:
        return request.expected_version

    # --- what an operation answers, to a response ----------------------------

    @staticmethod
    def chess_session_to_start_response(
        session: ChessSession | None,
    ) -> chess_game_dto_pb2.StartGameResponse:
        """
        An unset session is how the schema says the table cannot start a game.
        """
        return chess_game_dto_pb2.StartGameResponse(session=session)

    @staticmethod
    def chess_session_to_read_response(
        session: ChessSession | None,
    ) -> chess_game_dto_pb2.ReadGameResponse:
        """
        An unset session is how the schema says no game is being played there.
        """
        return chess_game_dto_pb2.ReadGameResponse(session=session)

    @staticmethod
    def action_result_to_play_response(
        result: ActionResult,
    ) -> chess_game_dto_pb2.PlayActionResponse:
        return chess_game_dto_pb2.PlayActionResponse(result=result)

    # --- a pydantic model, to the message of the same contract ---------------

    @staticmethod
    def start_request_model_to_message(
        model: StartGameRequest,
    ) -> chess_game_dto_pb2.StartGameRequest:
        return ProtobufMessageUtils.message_from_pydantic_model(
            model, chess_game_dto_pb2.StartGameRequest
        )

    @staticmethod
    def start_response_message_to_model(
        message: chess_game_dto_pb2.StartGameResponse,
    ) -> StartGameResponse:
        return ProtobufMessageUtils.message_to_pydantic_model(message, StartGameResponse)

    @staticmethod
    def read_request_model_to_message(
        model: ReadGameRequest,
    ) -> chess_game_dto_pb2.ReadGameRequest:
        return ProtobufMessageUtils.message_from_pydantic_model(
            model, chess_game_dto_pb2.ReadGameRequest
        )

    @staticmethod
    def read_response_message_to_model(
        message: chess_game_dto_pb2.ReadGameResponse,
    ) -> ReadGameResponse:
        return ProtobufMessageUtils.message_to_pydantic_model(message, ReadGameResponse)

    @staticmethod
    def play_request_model_to_message(
        model: PlayActionRequest,
    ) -> chess_game_dto_pb2.PlayActionRequest:
        return ProtobufMessageUtils.message_from_pydantic_model(
            model, chess_game_dto_pb2.PlayActionRequest
        )

    @staticmethod
    def play_response_message_to_model(
        message: chess_game_dto_pb2.PlayActionResponse,
    ) -> PlayActionResponse:
        return ProtobufMessageUtils.message_to_pydantic_model(message, PlayActionResponse)

    # --- a table, to the participants of the game played at it ---------------

    @staticmethod
    def table_to_participants(table: Table) -> tuple[Participant, ...]:
        """
        One participant per occupied seat, numbered as the seat is and carrying
        the role the seat was taken with.
        """
        return tuple(
            Participant(
                number=seat.number,
                player_id=seat.player_id,
                role=seat.role if seat.HasField("role") else None,
            )
            for seat in table.seats
            if seat.status == SeatStatus.SEAT_STATUS_OCCUPIED
        )

    # --- an action, to what the platform carries ----------------------------

    @staticmethod
    def chess_action_to_payload(action: ChessAction) -> any_pb2.Any:
        payload = any_pb2.Any()
        payload.Pack(action)
        return payload

    # --- the platform's answer, to chess's ----------------------------------

    @staticmethod
    def session_view_to_chess_session(view: SessionView) -> ChessSession | None:
        """
        The session with its game opened and its viewer named by colour, or None
        when the game it carries is not chess.
        """
        game = game_pb2.ChessGame()
        if not view.state.payload.Unpack(game):
            return None
        return ChessSession(
            id=view.id,
            game=game,
            color=ChessSessionAdapters.participant_to_color(game.roster, view.participant),
            last_command_id=view.last_command_id,
            version=view.version,
        )

    @staticmethod
    def command_result_to_action_result(result: CommandResult) -> ActionResult:
        """
        The session is carried whatever the outcome, and stays unset when the
        platform answered none or the game it carries is not chess.
        """
        session = (
            ChessSessionAdapters.session_view_to_chess_session(result.session)
            if result.HasField("session")
            else None
        )
        return ActionResult(outcome=result.outcome, session=session)

    @staticmethod
    def participant_to_color(roster: game_pb2.PlayerRoster, participant: int) -> piece_pb2.Color:
        """
        The side this participant plays, or unset for someone who is not playing.
        """
        if participant == roster.white.participant:
            return piece_pb2.COLOR_WHITE
        if participant == roster.black.participant:
            return piece_pb2.COLOR_BLACK
        return piece_pb2.COLOR_UNSPECIFIED
