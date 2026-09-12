import unittest

from tests.recording_client import RecordingClient
from websocket_server.controller.client_hub import ClientHub

TABLE_CHANNEL = "table:t-1"
LOBBY_CHANNEL = "lobby"
FRAME = b"frame"


class ClientHubTest(unittest.TestCase):
    """
    Who is held under which channel, and who a broadcast reaches.
    """

    def setUp(self) -> None:
        self.hub = ClientHub()

    def test_a_broadcast_reaches_every_watcher_of_the_channel_and_no_other(self) -> None:
        first = RecordingClient()
        second = RecordingClient()
        elsewhere = RecordingClient()
        self.hub.attach(TABLE_CHANNEL, first)
        self.hub.attach(TABLE_CHANNEL, second)
        self.hub.attach(LOBBY_CHANNEL, elsewhere)
        self.hub.broadcast(TABLE_CHANNEL, FRAME)
        self.assertEqual(first.frames, [FRAME])
        self.assertEqual(second.frames, [FRAME])
        self.assertEqual(elsewhere.frames, [])

    def test_a_broadcast_on_a_channel_nobody_watches_reaches_nobody(self) -> None:
        self.hub.broadcast(TABLE_CHANNEL, FRAME)
        self.assertEqual(self.hub.get_watched_channels(), frozenset())

    def test_watchers_are_counted_per_channel(self) -> None:
        client = RecordingClient()
        self.hub.attach(TABLE_CHANNEL, client)
        self.hub.attach(TABLE_CHANNEL, client)
        self.assertEqual(self.hub.get_watcher_count(TABLE_CHANNEL), 1)
        self.hub.attach(TABLE_CHANNEL, RecordingClient())
        self.assertEqual(self.hub.get_watcher_count(TABLE_CHANNEL), 2)
        self.assertEqual(self.hub.get_watcher_count(LOBBY_CHANNEL), 0)

    def test_the_last_detach_forgets_the_channel(self) -> None:
        client = RecordingClient()
        self.hub.attach(TABLE_CHANNEL, client)
        self.hub.detach(TABLE_CHANNEL, client)
        self.assertEqual(self.hub.get_watcher_count(TABLE_CHANNEL), 0)
        self.assertEqual(self.hub.get_watched_channels(), frozenset())
        self.hub.broadcast(TABLE_CHANNEL, FRAME)
        self.assertEqual(client.frames, [])

    def test_detaching_a_client_that_was_not_attached_changes_nothing(self) -> None:
        watching = RecordingClient()
        self.hub.attach(TABLE_CHANNEL, watching)
        self.hub.detach(TABLE_CHANNEL, RecordingClient())
        self.hub.detach(LOBBY_CHANNEL, watching)
        self.assertEqual(self.hub.get_watcher_count(TABLE_CHANNEL), 1)
