import asyncio
import unittest

from core.queue.message_utils import QueueMessageUtils
from core.queue.received_message import ReceivedMessage
from google.protobuf.wrappers_pb2 import StringValue
from idl.core.dto.websocket_pb2 import WebsocketMessageEnvelope
from idl.game.model.event_pb2 import CommandApplied, SessionChanged
from idl.lobby.model.event_pb2 import SeatTaken, TableChanged, TableClosed

from tests.in_memory_queue_consumer import InMemoryQueueConsumer
from tests.recording_client import RecordingClient
from websocket_server.controller.client_hub import ClientHub
from websocket_server.controller.subscription_controller import SubscriptionController

TABLE_ID = "t-1"
TABLE_CHANNEL = "table:t-1"
LOBBY_CHANNEL = "lobby"
VERSION = 8
CLOSED_VERSION = 0
SETTLE_SECONDS = 0.02


def seat_taken_on(channel: str) -> ReceivedMessage:
    event = SeatTaken(table_id=TABLE_ID, player_id="p-1", seat_number=1, version=VERSION)
    return ReceivedMessage(channel=channel, envelope=QueueMessageUtils.pack(event))


def command_applied_on(channel: str) -> ReceivedMessage:
    event = CommandApplied(session_id=TABLE_ID, participant=1, command_id="c-1", version=VERSION)
    return ReceivedMessage(channel=channel, envelope=QueueMessageUtils.pack(event))


def table_closed_on(channel: str) -> ReceivedMessage:
    return ReceivedMessage(
        channel=channel, envelope=QueueMessageUtils.pack(TableClosed(table_id=TABLE_ID))
    )


def frame_from(data: bytes) -> WebsocketMessageEnvelope:
    frame = WebsocketMessageEnvelope()
    frame.ParseFromString(data)
    return frame


class WatchingTest(unittest.IsolatedAsyncioTestCase):
    """
    When a source is subscribed and unsubscribed, as clients come and go.
    """

    def setUp(self) -> None:
        self.source = InMemoryQueueConsumer()
        self.other_source = InMemoryQueueConsumer()
        self.controller = SubscriptionController(
            hub=ClientHub(), sources=[self.source, self.other_source]
        )

    async def test_the_first_watcher_subscribes_every_source(self) -> None:
        await self.controller.attach(TABLE_CHANNEL, RecordingClient())
        self.assertEqual(self.source.subscribed, [TABLE_CHANNEL])
        self.assertEqual(self.other_source.subscribed, [TABLE_CHANNEL])

    async def test_the_second_watcher_does_not_subscribe_again(self) -> None:
        await self.controller.attach(TABLE_CHANNEL, RecordingClient())
        await self.controller.attach(TABLE_CHANNEL, RecordingClient())
        self.assertEqual(self.source.subscribed, [TABLE_CHANNEL])

    async def test_only_the_last_detach_unsubscribes(self) -> None:
        first = RecordingClient()
        second = RecordingClient()
        await self.controller.attach(TABLE_CHANNEL, first)
        await self.controller.attach(TABLE_CHANNEL, second)
        await self.controller.detach(TABLE_CHANNEL, first)
        self.assertEqual(self.source.unsubscribed, [])
        await self.controller.detach(TABLE_CHANNEL, second)
        self.assertEqual(self.source.unsubscribed, [TABLE_CHANNEL])
        self.assertEqual(self.other_source.unsubscribed, [TABLE_CHANNEL])

    async def test_channels_are_subscribed_independently(self) -> None:
        await self.controller.attach(TABLE_CHANNEL, RecordingClient())
        await self.controller.attach(LOBBY_CHANNEL, RecordingClient())
        self.assertEqual(self.source.subscribed, [TABLE_CHANNEL, LOBBY_CHANNEL])


class RelayTest(unittest.IsolatedAsyncioTestCase):
    """
    What a message on a channel becomes, and who it reaches.
    """

    def setUp(self) -> None:
        self.source = InMemoryQueueConsumer()
        self.controller = SubscriptionController(hub=ClientHub(), sources=[self.source])

    async def test_both_watchers_of_a_table_receive_the_frame(self) -> None:
        first = RecordingClient()
        second = RecordingClient()
        await self.controller.attach(TABLE_CHANNEL, first)
        await self.controller.attach(TABLE_CHANNEL, second)
        self.controller.relay(command_applied_on(TABLE_CHANNEL))
        self.assertEqual(len(first.frames), 1)
        self.assertEqual(first.frames, second.frames)
        changed = SessionChanged()
        self.assertTrue(frame_from(first.frames[0]).payload.Unpack(changed))
        self.assertEqual(changed.session_id, TABLE_ID)
        self.assertEqual(changed.version, VERSION)

    async def test_a_message_reaches_only_the_channel_it_arrived_on(self) -> None:
        at_table = RecordingClient()
        in_lobby = RecordingClient()
        await self.controller.attach(TABLE_CHANNEL, at_table)
        await self.controller.attach(LOBBY_CHANNEL, in_lobby)
        self.controller.relay(seat_taken_on(LOBBY_CHANNEL))
        self.assertEqual(at_table.frames, [])
        self.assertEqual(len(in_lobby.frames), 1)
        changed = TableChanged()
        self.assertTrue(frame_from(in_lobby.frames[0]).payload.Unpack(changed))
        self.assertEqual(changed.version, VERSION)

    async def test_a_closed_table_is_version_zero(self) -> None:
        client = RecordingClient()
        await self.controller.attach(LOBBY_CHANNEL, client)
        self.controller.relay(table_closed_on(LOBBY_CHANNEL))
        changed = TableChanged()
        self.assertTrue(frame_from(client.frames[0]).payload.Unpack(changed))
        self.assertEqual(changed.table_id, TABLE_ID)
        self.assertEqual(changed.version, CLOSED_VERSION)

    async def test_a_type_this_build_does_not_know_is_dropped(self) -> None:
        client = RecordingClient()
        await self.controller.attach(TABLE_CHANNEL, client)
        unknown = ReceivedMessage(
            channel=TABLE_CHANNEL, envelope=QueueMessageUtils.pack(StringValue(value="?"))
        )
        self.controller.relay(unknown)
        self.assertEqual(client.frames, [])

    async def test_a_detached_client_receives_nothing_more(self) -> None:
        client = RecordingClient()
        await self.controller.attach(TABLE_CHANNEL, client)
        await self.controller.detach(TABLE_CHANNEL, client)
        self.controller.relay(command_applied_on(TABLE_CHANNEL))
        self.assertEqual(client.frames, [])


class RunningTest(unittest.IsolatedAsyncioTestCase):
    """
    The relay over a running source, from start to close.
    """

    async def test_a_delivered_message_is_relayed_and_close_releases_the_source(self) -> None:
        source = InMemoryQueueConsumer()
        controller = SubscriptionController(hub=ClientHub(), sources=[source])
        client = RecordingClient()
        await controller.attach(TABLE_CHANNEL, client)
        await controller.start()
        await source.deliver(command_applied_on(TABLE_CHANNEL))
        await asyncio.sleep(SETTLE_SECONDS)
        self.assertEqual(len(client.frames), 1)
        await controller.close()
        self.assertTrue(source.closed)
