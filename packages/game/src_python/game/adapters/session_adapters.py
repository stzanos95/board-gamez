"""
Sessions, between the shapes a session takes.

A request carries what an operation needs; a controller takes those arguments and
answers with the domain's own types. Turning one into the other is what a servicer
delegates here, so no layer above the controller reads a field off a request.

A contract also produces two families of type — protobuf messages for gRPC and
pydantic models for HTTP — and a caller crossing between them converts here too.

A session is stored under a shape of its own, which carries identity and version
in metadata, and is answered to a client under another, projected for one
participant. Both conversions run here.

One method per direction, named for it. A caller reaches for the one it needs and
sees the types on both sides; nothing here is chosen at run time.
"""

from datetime import datetime

from core.protobuf.message_utils import ProtobufMessageUtils
from google.protobuf import any_pb2
from google.protobuf.timestamp_pb2 import Timestamp
from idl.core.obj.object_metadata_pb2 import ObjectMetadata
from idl.game.dto import command_pb2, session_pb2
from idl.game.model.command_result_pb2 import CommandResult
from idl.game.model.game_state_pb2 import GameState
from idl.game.model.game_type_pb2 import GameType
from idl.game.model.participant_pb2 import Participant, ParticipantRole
from idl.game.model.session_pb2 import Session, SessionView
from idl.game.model.withdrawal_result_pb2 import WithdrawalResult
from idl.game.obj.session_pb2 import SessionObj
from idl_fastapi.idl.game.dto import (
    ApplyCommandRequest,
    ApplyCommandResponse,
    CreateSessionRequest,
    CreateSessionResponse,
    ReadSessionRequest,
    ReadSessionResponse,
    WithdrawPlayerRequest,
    WithdrawPlayerResponse,
)


class SessionAdapters:
    """
    Every SessionService message, converted to what the layer beneath it takes.
    """

    # --- a request, to the arguments an operation takes ----------------------

    @staticmethod
    def create_request_to_table_id(request: session_pb2.CreateSessionRequest) -> str:
        return request.table_id

    @staticmethod
    def create_request_to_player_id(request: session_pb2.CreateSessionRequest) -> str:
        return request.player_id

    @staticmethod
    def create_request_to_game_type(
        request: session_pb2.CreateSessionRequest,
    ) -> GameType:
        return request.game_type

    @staticmethod
    def create_request_to_participants(
        request: session_pb2.CreateSessionRequest,
    ) -> tuple[Participant, ...]:
        return tuple(request.participants)

    # --- participants, to what a game's rules are told ----------------------

    @staticmethod
    def participants_to_participant_roles(
        participants: tuple[Participant, ...],
    ) -> tuple[ParticipantRole, ...]:
        """
        Each participant's number and role, with the player id left behind.
        """
        return tuple(
            ParticipantRole(
                participant=participant.number,
                role=participant.role if participant.HasField("role") else None,
            )
            for participant in participants
        )

    @staticmethod
    def read_request_to_session_id(request: session_pb2.ReadSessionRequest) -> str:
        return request.session_id

    @staticmethod
    def read_request_to_player_id(request: session_pb2.ReadSessionRequest) -> str:
        return request.player_id

    @staticmethod
    def apply_request_to_session_id(request: command_pb2.ApplyCommandRequest) -> str:
        return request.session_id

    @staticmethod
    def apply_request_to_player_id(request: command_pb2.ApplyCommandRequest) -> str:
        return request.player_id

    @staticmethod
    def apply_request_to_command_id(request: command_pb2.ApplyCommandRequest) -> str:
        return request.command_id

    @staticmethod
    def apply_request_to_action(request: command_pb2.ApplyCommandRequest) -> any_pb2.Any:
        return request.action

    @staticmethod
    def apply_request_to_expected_version(request: command_pb2.ApplyCommandRequest) -> int:
        return request.expected_version

    @staticmethod
    def withdraw_request_to_session_id(request: session_pb2.WithdrawPlayerRequest) -> str:
        return request.session_id

    @staticmethod
    def withdraw_request_to_player_id(request: session_pb2.WithdrawPlayerRequest) -> str:
        return request.player_id

    # --- what an operation answers, to a response ----------------------------

    @staticmethod
    def session_view_to_create_response(
        session: SessionView | None,
    ) -> session_pb2.CreateSessionResponse:
        """
        An unset session is how the schema says the game refused the roster.
        """
        return session_pb2.CreateSessionResponse(session=session)

    @staticmethod
    def session_view_to_read_response(
        session: SessionView | None,
    ) -> session_pb2.ReadSessionResponse:
        """
        An unset session is how the schema says no game has that id.
        """
        return session_pb2.ReadSessionResponse(session=session)

    @staticmethod
    def command_result_to_apply_response(
        result: CommandResult,
    ) -> command_pb2.ApplyCommandResponse:
        return command_pb2.ApplyCommandResponse(result=result)

    @staticmethod
    def withdrawal_result_to_withdraw_response(
        result: WithdrawalResult,
    ) -> session_pb2.WithdrawPlayerResponse:
        return session_pb2.WithdrawPlayerResponse(result=result)

    # --- a pydantic model, to the message of the same contract ---------------

    @staticmethod
    def create_request_model_to_message(
        model: CreateSessionRequest,
    ) -> session_pb2.CreateSessionRequest:
        return ProtobufMessageUtils.message_from_pydantic_model(
            model, session_pb2.CreateSessionRequest
        )

    @staticmethod
    def create_response_message_to_model(
        message: session_pb2.CreateSessionResponse,
    ) -> CreateSessionResponse:
        return ProtobufMessageUtils.message_to_pydantic_model(message, CreateSessionResponse)

    @staticmethod
    def read_request_model_to_message(model: ReadSessionRequest) -> session_pb2.ReadSessionRequest:
        return ProtobufMessageUtils.message_from_pydantic_model(
            model, session_pb2.ReadSessionRequest
        )

    @staticmethod
    def read_response_message_to_model(
        message: session_pb2.ReadSessionResponse,
    ) -> ReadSessionResponse:
        return ProtobufMessageUtils.message_to_pydantic_model(message, ReadSessionResponse)

    @staticmethod
    def apply_request_model_to_message(
        model: ApplyCommandRequest,
    ) -> command_pb2.ApplyCommandRequest:
        return ProtobufMessageUtils.message_from_pydantic_model(
            model, command_pb2.ApplyCommandRequest
        )

    @staticmethod
    def apply_response_message_to_model(
        message: command_pb2.ApplyCommandResponse,
    ) -> ApplyCommandResponse:
        return ProtobufMessageUtils.message_to_pydantic_model(message, ApplyCommandResponse)

    @staticmethod
    def withdraw_request_model_to_message(
        model: WithdrawPlayerRequest,
    ) -> session_pb2.WithdrawPlayerRequest:
        return ProtobufMessageUtils.message_from_pydantic_model(
            model, session_pb2.WithdrawPlayerRequest
        )

    @staticmethod
    def withdraw_response_message_to_model(
        message: session_pb2.WithdrawPlayerResponse,
    ) -> WithdrawPlayerResponse:
        return ProtobufMessageUtils.message_to_pydantic_model(message, WithdrawPlayerResponse)

    # --- a session, to what a store holds, and back --------------------------

    @staticmethod
    def session_to_session_obj(session: Session) -> SessionObj:
        """
        The session to hand a store.

        The timestamps stay unset: a write time is known to whatever writes.
        """
        return SessionObj(
            metadata=ObjectMetadata(id=session.id, version=session.version),
            game_type=session.game_type,
            participants=session.participants,
            state=session.state,
            last_command_id=session.last_command_id,
            acts_by=session.acts_by if session.HasField("acts_by") else None,
        )

    @staticmethod
    def session_obj_to_session(stored: SessionObj) -> Session:
        return Session(
            id=stored.metadata.id,
            game_type=stored.game_type,
            participants=stored.participants,
            state=stored.state,
            last_command_id=stored.last_command_id,
            version=stored.metadata.version,
            acts_by=stored.acts_by if stored.HasField("acts_by") else None,
        )

    # --- a state and the time it was written, to when it runs out -----------

    @staticmethod
    def state_to_acts_by(state: GameState, written_at: datetime) -> Timestamp | None:
        """
        The instant the state's `acts_within` runs out, measured from this
        write, or None when the state carries none.
        """
        if not state.HasField("acts_within"):
            return None
        acts_by = Timestamp()
        acts_by.FromDatetime(written_at + state.acts_within.ToTimedelta())
        return acts_by

    @staticmethod
    def datetime_to_timestamp(instant: datetime) -> Timestamp:
        timestamp = Timestamp()
        timestamp.FromDatetime(instant)
        return timestamp

    # --- a session, to what one participant is answered with ----------------

    @staticmethod
    def session_to_session_view(
        session: Session, participant: int, projected_payload: any_pb2.Any
    ) -> SessionView:
        """
        The session as this participant may see it.

        `projected_payload` is the game as its rules projected it for the
        participant, and replaces the whole game the session holds.
        """
        return SessionView(
            id=session.id,
            game_type=session.game_type,
            participants=session.participants,
            participant=participant,
            state=GameState(
                payload=projected_payload,
                participants_to_act=session.state.participants_to_act,
                result=session.state.result if session.state.HasField("result") else None,
                acts_within=(
                    session.state.acts_within if session.state.HasField("acts_within") else None
                ),
                participant_statuses=session.state.participant_statuses,
            ),
            last_command_id=session.last_command_id,
            version=session.version,
            acts_by=session.acts_by if session.HasField("acts_by") else None,
        )
