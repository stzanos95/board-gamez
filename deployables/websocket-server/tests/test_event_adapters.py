import unittest

from core.queue.message_utils import QueueMessageUtils
from google.protobuf.wrappers_pb2 import StringValue
from idl.core.dto.queue_pb2 import QueueMessageEnvelope
from idl.game.model.event_pb2 import (
    CommandApplied,
    DeadlineExpired,
    ParticipantWithdrawn,
    SessionChanged,
    SessionStarted,
)
from idl.game.model.game_type_pb2 import GameType
from idl.lobby.model.event_pb2 import (
    PlayerJoined,
    PlayerLeft,
    SeatTaken,
    SeatVacated,
    TableChanged,
    TableClosed,
    TableCreated,
    TableStarted,
)

from websocket_server.adapters.event_adapters import EventAdapters

TABLE_ID = "t-1"
PLAYER_ID = "p-1"
SEAT_NUMBER = 2
PARTICIPANT = 1
VERSION = 7
CLOSED_VERSION = 0
SESSION_CHANGED_TYPE = "idl.game.model.SessionChanged"
TABLE_CHANGED_TYPE = "idl.lobby.model.TableChanged"


def session_changed_from(envelope: QueueMessageEnvelope) -> SessionChanged:
    frame = EventAdapters.envelope_to_frame(envelope)
    assert frame is not None
    changed = SessionChanged()
    assert frame.payload.Unpack(changed)
    assert frame.header.type == SESSION_CHANGED_TYPE
    return changed


def table_changed_from(envelope: QueueMessageEnvelope) -> TableChanged:
    frame = EventAdapters.envelope_to_frame(envelope)
    assert frame is not None
    changed = TableChanged()
    assert frame.payload.Unpack(changed)
    assert frame.header.type == TABLE_CHANGED_TYPE
    return changed


class GameEventTest(unittest.TestCase):
    """
    Every game event becomes a SessionChanged carrying the event's version.
    """

    def test_session_started(self) -> None:
        event = SessionStarted(
            session_id=TABLE_ID, game_type=GameType.GAME_TYPE_CHESS, version=VERSION
        )
        changed = session_changed_from(QueueMessageUtils.pack(event))
        self.assertEqual(changed.session_id, TABLE_ID)
        self.assertEqual(changed.version, VERSION)

    def test_command_applied(self) -> None:
        event = CommandApplied(
            session_id=TABLE_ID, participant=PARTICIPANT, command_id="c-1", version=VERSION
        )
        event.action.Pack(StringValue(value="only the sender may see this"))
        frame = EventAdapters.envelope_to_frame(QueueMessageUtils.pack(event))
        assert frame is not None
        changed = session_changed_from(QueueMessageUtils.pack(event))
        self.assertEqual(changed.version, VERSION)
        self.assertNotIn(b"only the sender", frame.SerializeToString())

    def test_deadline_expired(self) -> None:
        event = DeadlineExpired(session_id=TABLE_ID, is_over=True, version=VERSION)
        changed = session_changed_from(QueueMessageUtils.pack(event))
        self.assertEqual(changed.session_id, TABLE_ID)
        self.assertEqual(changed.version, VERSION)

    def test_participant_withdrawn(self) -> None:
        event = ParticipantWithdrawn(
            session_id=TABLE_ID, participant=PARTICIPANT, is_over=True, version=VERSION
        )
        changed = session_changed_from(QueueMessageUtils.pack(event))
        self.assertEqual(changed.session_id, TABLE_ID)
        self.assertEqual(changed.version, VERSION)


class TableEventTest(unittest.TestCase):
    """
    Every table event becomes a TableChanged carrying the event's version, and
    a closed table is version 0.
    """

    def test_table_created(self) -> None:
        event = TableCreated(
            table_id=TABLE_ID,
            game_type=GameType.GAME_TYPE_CHESS,
            player_id=PLAYER_ID,
            version=VERSION,
        )
        changed = table_changed_from(QueueMessageUtils.pack(event))
        self.assertEqual(changed.table_id, TABLE_ID)
        self.assertEqual(changed.version, VERSION)

    def test_player_joined(self) -> None:
        event = PlayerJoined(table_id=TABLE_ID, player_id=PLAYER_ID, version=VERSION)
        self.assertEqual(table_changed_from(QueueMessageUtils.pack(event)).version, VERSION)

    def test_seat_taken(self) -> None:
        event = SeatTaken(
            table_id=TABLE_ID, player_id=PLAYER_ID, seat_number=SEAT_NUMBER, version=VERSION
        )
        self.assertEqual(table_changed_from(QueueMessageUtils.pack(event)).version, VERSION)

    def test_seat_vacated(self) -> None:
        event = SeatVacated(
            table_id=TABLE_ID, player_id=PLAYER_ID, seat_number=SEAT_NUMBER, version=VERSION
        )
        self.assertEqual(table_changed_from(QueueMessageUtils.pack(event)).version, VERSION)

    def test_player_left(self) -> None:
        event = PlayerLeft(
            table_id=TABLE_ID, player_id=PLAYER_ID, seat_number=SEAT_NUMBER, version=VERSION
        )
        self.assertEqual(table_changed_from(QueueMessageUtils.pack(event)).version, VERSION)

    def test_table_started(self) -> None:
        event = TableStarted(table_id=TABLE_ID, version=VERSION)
        self.assertEqual(table_changed_from(QueueMessageUtils.pack(event)).version, VERSION)

    def test_table_closed_is_version_zero(self) -> None:
        changed = table_changed_from(QueueMessageUtils.pack(TableClosed(table_id=TABLE_ID)))
        self.assertEqual(changed.table_id, TABLE_ID)
        self.assertEqual(changed.version, CLOSED_VERSION)


class UnknownEventTest(unittest.TestCase):
    def test_a_type_this_build_does_not_know_is_dropped(self) -> None:
        envelope = QueueMessageUtils.pack(StringValue(value="not an event"))
        self.assertIsNone(EventAdapters.envelope_to_frame(envelope))

    def test_a_payload_that_is_not_what_the_header_says_is_dropped(self) -> None:
        envelope = QueueMessageUtils.pack(StringValue(value="not a seat"))
        envelope.header.type = SeatTaken.DESCRIPTOR.full_name
        self.assertIsNone(EventAdapters.envelope_to_frame(envelope))

    def test_every_frame_carries_a_fresh_id(self) -> None:
        envelope = QueueMessageUtils.pack(TableClosed(table_id=TABLE_ID))
        first = EventAdapters.envelope_to_frame(envelope)
        second = EventAdapters.envelope_to_frame(envelope)
        assert first is not None and second is not None
        self.assertNotEqual(first.header.id, second.header.id)
