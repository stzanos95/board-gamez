"""
Events, to the frame a browser is sent.

The only place an event is opened, and it is opened only to read an id and a
version. Every table event becomes a TableChanged and every game event becomes
a SessionChanged; nothing else an event carries reaches a socket.
"""

from collections.abc import Callable
from typing import ClassVar

from core.protobuf.message_utils import ProtobufMessageUtils
from core.websocket.message_utils import WebsocketMessageUtils
from google.protobuf.message import Message
from idl.core.dto.queue_pb2 import QueueMessageEnvelope
from idl.core.dto.websocket_pb2 import WebsocketMessageEnvelope
from idl.game.model.event_pb2 import (
    CommandApplied,
    ParticipantWithdrawn,
    SessionChanged,
    SessionStarted,
)
from idl.lobby.model.event_pb2 import (
    PlayerJoined,
    PlayerLeft,
    SeatTaken,
    SeatVacated,
    TableChanged,
    TableClosed,
    TableCreated,
)

CLOSED_TABLE_VERSION = 0

FrameBuilder = Callable[[QueueMessageEnvelope], Message | None]


class EventAdapters:
    """
    Every event this build knows, converted to the frame it is sent as.
    """

    @staticmethod
    def envelope_to_frame(envelope: QueueMessageEnvelope) -> WebsocketMessageEnvelope | None:
        """
        The frame this event is sent as, or None when the event is of a type
        this build does not know or its payload is not what its header says.
        """
        builder = EventAdapters.FRAME_BUILDERS_BY_EVENT_TYPE.get(envelope.header.type)
        if builder is None:
            return None
        frame = builder(envelope)
        if frame is None:
            return None
        return WebsocketMessageUtils.pack(frame)

    # --- game events, to SessionChanged ---------------------------------------

    @staticmethod
    def _session_started_to_session_changed(envelope: QueueMessageEnvelope) -> Message | None:
        event = ProtobufMessageUtils.message_from_any(envelope.payload, SessionStarted)
        if event is None:
            return None
        return SessionChanged(session_id=event.session_id, version=event.version)

    @staticmethod
    def _command_applied_to_session_changed(envelope: QueueMessageEnvelope) -> Message | None:
        event = ProtobufMessageUtils.message_from_any(envelope.payload, CommandApplied)
        if event is None:
            return None
        return SessionChanged(session_id=event.session_id, version=event.version)

    @staticmethod
    def _participant_withdrawn_to_session_changed(
        envelope: QueueMessageEnvelope,
    ) -> Message | None:
        event = ProtobufMessageUtils.message_from_any(envelope.payload, ParticipantWithdrawn)
        if event is None:
            return None
        return SessionChanged(session_id=event.session_id, version=event.version)

    # --- table events, to TableChanged ----------------------------------------

    @staticmethod
    def _table_created_to_table_changed(envelope: QueueMessageEnvelope) -> Message | None:
        event = ProtobufMessageUtils.message_from_any(envelope.payload, TableCreated)
        if event is None:
            return None
        return TableChanged(table_id=event.table_id, version=event.version)

    @staticmethod
    def _player_joined_to_table_changed(envelope: QueueMessageEnvelope) -> Message | None:
        event = ProtobufMessageUtils.message_from_any(envelope.payload, PlayerJoined)
        if event is None:
            return None
        return TableChanged(table_id=event.table_id, version=event.version)

    @staticmethod
    def _seat_taken_to_table_changed(envelope: QueueMessageEnvelope) -> Message | None:
        event = ProtobufMessageUtils.message_from_any(envelope.payload, SeatTaken)
        if event is None:
            return None
        return TableChanged(table_id=event.table_id, version=event.version)

    @staticmethod
    def _seat_vacated_to_table_changed(envelope: QueueMessageEnvelope) -> Message | None:
        event = ProtobufMessageUtils.message_from_any(envelope.payload, SeatVacated)
        if event is None:
            return None
        return TableChanged(table_id=event.table_id, version=event.version)

    @staticmethod
    def _player_left_to_table_changed(envelope: QueueMessageEnvelope) -> Message | None:
        event = ProtobufMessageUtils.message_from_any(envelope.payload, PlayerLeft)
        if event is None:
            return None
        return TableChanged(table_id=event.table_id, version=event.version)

    @staticmethod
    def _table_closed_to_table_changed(envelope: QueueMessageEnvelope) -> Message | None:
        """
        A closed table has no version after it, and version 0 is how the frame
        says so.
        """
        event = ProtobufMessageUtils.message_from_any(envelope.payload, TableClosed)
        if event is None:
            return None
        return TableChanged(table_id=event.table_id, version=CLOSED_TABLE_VERSION)

    # Keys are data — an event's full type name names the builder of its frame.
    FRAME_BUILDERS_BY_EVENT_TYPE: ClassVar[dict[str, FrameBuilder]] = {
        SessionStarted.DESCRIPTOR.full_name: _session_started_to_session_changed,
        CommandApplied.DESCRIPTOR.full_name: _command_applied_to_session_changed,
        ParticipantWithdrawn.DESCRIPTOR.full_name: _participant_withdrawn_to_session_changed,
        TableCreated.DESCRIPTOR.full_name: _table_created_to_table_changed,
        PlayerJoined.DESCRIPTOR.full_name: _player_joined_to_table_changed,
        SeatTaken.DESCRIPTOR.full_name: _seat_taken_to_table_changed,
        SeatVacated.DESCRIPTOR.full_name: _seat_vacated_to_table_changed,
        PlayerLeft.DESCRIPTOR.full_name: _player_left_to_table_changed,
        TableClosed.DESCRIPTOR.full_name: _table_closed_to_table_changed,
    }
