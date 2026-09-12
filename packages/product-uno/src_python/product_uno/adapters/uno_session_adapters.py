"""
A game of UNO being played, between the shapes it takes.

A request carries what an operation needs; a controller takes those arguments and
answers with UNO's own types. Turning one into the other is what a servicer
delegates here, so no layer above the controller reads a field off a request.

A contract also produces two families of type — protobuf messages for gRPC and
pydantic models for HTTP — and a caller crossing between them converts here too.

The platform answers a session with the viewer's projection packed opaquely and
the viewer named by participant number. Opening the projection into a
UnoSession runs here.
"""

from core.protobuf.message_utils import ProtobufMessageUtils
from google.protobuf import any_pb2
from idl.game.model.command_result_pb2 import CommandResult
from idl.game.model.participant_pb2 import Participant
from idl.game.model.session_pb2 import SessionView
from idl.lobby.model.seat_pb2 import SeatStatus
from idl.lobby.model.table_pb2 import Table
from idl.uno.dto import game_pb2 as uno_game_dto_pb2
from idl.uno.model.action_pb2 import UnoAction
from idl.uno.model.session_pb2 import ActionResult, UnoSession
from idl.uno.model.view_pb2 import UnoView
from idl_fastapi.idl.uno.dto import (
    PlayActionRequest,
    PlayActionResponse,
    ReadGameRequest,
    ReadGameResponse,
    StartGameRequest,
    StartGameResponse,
)


class UnoSessionAdapters:
    """
    Every UnoService message and every platform type, converted to what the
    layer beneath it takes.
    """

    # --- a request, to the arguments an operation takes ----------------------

    @staticmethod
    def start_request_to_table_id(request: uno_game_dto_pb2.StartGameRequest) -> str:
        return request.table_id

    @staticmethod
    def start_request_to_player_id(request: uno_game_dto_pb2.StartGameRequest) -> str:
        return request.player_id

    @staticmethod
    def read_request_to_table_id(request: uno_game_dto_pb2.ReadGameRequest) -> str:
        return request.table_id

    @staticmethod
    def read_request_to_player_id(request: uno_game_dto_pb2.ReadGameRequest) -> str:
        return request.player_id

    @staticmethod
    def play_request_to_table_id(request: uno_game_dto_pb2.PlayActionRequest) -> str:
        return request.table_id

    @staticmethod
    def play_request_to_player_id(request: uno_game_dto_pb2.PlayActionRequest) -> str:
        return request.player_id

    @staticmethod
    def play_request_to_command_id(request: uno_game_dto_pb2.PlayActionRequest) -> str:
        return request.command_id

    @staticmethod
    def play_request_to_action(request: uno_game_dto_pb2.PlayActionRequest) -> UnoAction:
        return request.action

    @staticmethod
    def play_request_to_expected_version(request: uno_game_dto_pb2.PlayActionRequest) -> int:
        return request.expected_version

    # --- what an operation answers, to a response ----------------------------

    @staticmethod
    def uno_session_to_start_response(
        session: UnoSession | None,
    ) -> uno_game_dto_pb2.StartGameResponse:
        """
        An unset session is how the schema says the table cannot start a game.
        """
        return uno_game_dto_pb2.StartGameResponse(session=session)

    @staticmethod
    def uno_session_to_read_response(
        session: UnoSession | None,
    ) -> uno_game_dto_pb2.ReadGameResponse:
        """
        An unset session is how the schema says no game is being played there.
        """
        return uno_game_dto_pb2.ReadGameResponse(session=session)

    @staticmethod
    def action_result_to_play_response(
        result: ActionResult,
    ) -> uno_game_dto_pb2.PlayActionResponse:
        return uno_game_dto_pb2.PlayActionResponse(result=result)

    # --- a pydantic model, to the message of the same contract ---------------

    @staticmethod
    def start_request_model_to_message(
        model: StartGameRequest,
    ) -> uno_game_dto_pb2.StartGameRequest:
        return ProtobufMessageUtils.message_from_pydantic_model(
            model, uno_game_dto_pb2.StartGameRequest
        )

    @staticmethod
    def start_response_message_to_model(
        message: uno_game_dto_pb2.StartGameResponse,
    ) -> StartGameResponse:
        return ProtobufMessageUtils.message_to_pydantic_model(message, StartGameResponse)

    @staticmethod
    def read_request_model_to_message(
        model: ReadGameRequest,
    ) -> uno_game_dto_pb2.ReadGameRequest:
        return ProtobufMessageUtils.message_from_pydantic_model(
            model, uno_game_dto_pb2.ReadGameRequest
        )

    @staticmethod
    def read_response_message_to_model(
        message: uno_game_dto_pb2.ReadGameResponse,
    ) -> ReadGameResponse:
        return ProtobufMessageUtils.message_to_pydantic_model(message, ReadGameResponse)

    @staticmethod
    def play_request_model_to_message(
        model: PlayActionRequest,
    ) -> uno_game_dto_pb2.PlayActionRequest:
        return ProtobufMessageUtils.message_from_pydantic_model(
            model, uno_game_dto_pb2.PlayActionRequest
        )

    @staticmethod
    def play_response_message_to_model(
        message: uno_game_dto_pb2.PlayActionResponse,
    ) -> PlayActionResponse:
        return ProtobufMessageUtils.message_to_pydantic_model(message, PlayActionResponse)

    # --- a table, to the participants of the game played at it ---------------

    @staticmethod
    def table_to_participants(table: Table) -> tuple[Participant, ...]:
        """
        One participant per occupied seat, numbered as the seat is. A UNO seat
        carries no role.
        """
        return tuple(
            Participant(number=seat.number, player_id=seat.player_id)
            for seat in table.seats
            if seat.status == SeatStatus.SEAT_STATUS_OCCUPIED
        )

    # --- an action, to what the platform carries ----------------------------

    @staticmethod
    def uno_action_to_payload(action: UnoAction) -> any_pb2.Any:
        payload = any_pb2.Any()
        payload.Pack(action)
        return payload

    # --- the platform's answer, to UNO's ------------------------------------

    @staticmethod
    def session_view_to_uno_session(view: SessionView) -> UnoSession | None:
        """
        The session with its projection opened, or None when what it carries
        is not a UNO view.
        """
        uno_view = UnoView()
        if not view.state.payload.Unpack(uno_view):
            return None
        return UnoSession(
            id=view.id,
            view=uno_view,
            participant=view.participant,
            last_command_id=view.last_command_id,
            version=view.version,
            participant_statuses=view.state.participant_statuses,
        )

    @staticmethod
    def command_result_to_action_result(result: CommandResult) -> ActionResult:
        """
        The session is carried whatever the outcome, and stays unset when the
        platform answered none or the game it carries is not UNO.
        """
        session = (
            UnoSessionAdapters.session_view_to_uno_session(result.session)
            if result.HasField("session")
            else None
        )
        return ActionResult(outcome=result.outcome, session=session)
