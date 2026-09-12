import unittest

from core.queue.message_utils import QueueMessageUtils
from core.queue.received_message import ReceivedMessage
from idl.lobby.model.event_pb2 import SeatTaken

from tests.fake_socketify import FakeRequest, FakeResponse, FakeWebSocket
from tests.in_memory_queue_consumer import InMemoryQueueConsumer
from websocket_server.controller.client_hub import ClientHub
from websocket_server.controller.subscription_controller import SubscriptionController
from websocket_server.log_level import LogLevel
from websocket_server.service.socket_connection import SocketConnection
from websocket_server.service.socket_routes import HTTP_BAD_REQUEST, SocketRoutes
from websocket_server.service.websocket_behavior import (
    CLOSE_KEY,
    IDLE_TIMEOUT_KEY,
    MAX_PAYLOAD_LENGTH_KEY,
    OPEN_KEY,
    UPGRADE_KEY,
)
from websocket_server.websocket_server_config import ServerConfig

TABLE_ID = "t-1"
TABLE_CHANNEL = "table:t-1"
LOBBY_CHANNEL = "lobby"
IDLE_TIMEOUT = 60
MAX_PAYLOAD = 256
NORMAL_CLOSURE = 1000
HANDSHAKE_HEADERS = {
    "sec-websocket-key": "dGhlIHNhbXBsZSBub25jZQ==",
    "sec-websocket-protocol": "",
    "sec-websocket-extensions": "permessage-deflate",
}
SOCKET_CONTEXT = object()


def server_config() -> ServerConfig:
    return ServerConfig(
        host="127.0.0.1",
        port=8999,
        log_level=LogLevel.WARNING,
        idle_timeout_seconds=IDLE_TIMEOUT,
        max_payload_bytes=MAX_PAYLOAD,
    )


class SocketRoutesTest(unittest.IsolatedAsyncioTestCase):
    """
    A socket's life through a route: upgraded for a channel, attached on open,
    detached on close.
    """

    def setUp(self) -> None:
        self.source = InMemoryQueueConsumer()
        self.hub = ClientHub()
        self.controller = SubscriptionController(hub=self.hub, sources=[self.source])
        self.routes = SocketRoutes(self.controller)
        self.config = server_config()

    def test_the_behaviors_carry_the_configured_limits(self) -> None:
        behavior = self.routes.table_behavior(self.config).to_dict()
        self.assertEqual(behavior[IDLE_TIMEOUT_KEY], IDLE_TIMEOUT)
        self.assertEqual(behavior[MAX_PAYLOAD_LENGTH_KEY], MAX_PAYLOAD)
        self.assertTrue(callable(behavior[UPGRADE_KEY]))
        self.assertTrue(callable(behavior[OPEN_KEY]))
        self.assertTrue(callable(behavior[CLOSE_KEY]))

    def test_a_table_route_upgrades_for_the_table_channel(self) -> None:
        response = FakeResponse()
        self.routes.table_behavior(self.config).upgrade(
            response, FakeRequest({0: TABLE_ID}, HANDSHAKE_HEADERS), SOCKET_CONTEXT
        )
        connection = response.upgraded_with
        assert isinstance(connection, SocketConnection)
        self.assertEqual(connection.channel, TABLE_CHANNEL)
        self.assertIsNone(connection.client)
        self.assertEqual(response.key, HANDSHAKE_HEADERS["sec-websocket-key"])
        self.assertEqual(response.extensions, HANDSHAKE_HEADERS["sec-websocket-extensions"])

    def test_the_lobby_route_upgrades_for_the_lobby_channel(self) -> None:
        response = FakeResponse()
        self.routes.lobby_behavior(self.config).upgrade(
            response, FakeRequest({}, HANDSHAKE_HEADERS), SOCKET_CONTEXT
        )
        connection = response.upgraded_with
        assert isinstance(connection, SocketConnection)
        self.assertEqual(connection.channel, LOBBY_CHANNEL)

    def test_a_table_route_without_a_table_id_is_refused(self) -> None:
        response = FakeResponse()
        self.routes.table_behavior(self.config).upgrade(
            response, FakeRequest({}, HANDSHAKE_HEADERS), SOCKET_CONTEXT
        )
        self.assertIsNone(response.upgraded_with)
        self.assertEqual(response.status, HTTP_BAD_REQUEST)

    async def test_open_attaches_and_close_detaches(self) -> None:
        behavior = self.routes.table_behavior(self.config)
        websocket = FakeWebSocket(user_data=SocketConnection(channel=TABLE_CHANNEL))
        await behavior.open(websocket)
        self.assertEqual(self.hub.get_watcher_count(TABLE_CHANNEL), 1)
        self.assertEqual(self.source.subscribed, [TABLE_CHANNEL])

        event = SeatTaken(table_id=TABLE_ID, player_id="p-1", seat_number=1, version=3)
        self.controller.relay(
            ReceivedMessage(channel=TABLE_CHANNEL, envelope=QueueMessageUtils.pack(event))
        )
        self.assertEqual(len(websocket.sent), 1)

        await behavior.close(websocket, NORMAL_CLOSURE, None)
        self.assertEqual(self.hub.get_watcher_count(TABLE_CHANNEL), 0)
        self.assertEqual(self.source.unsubscribed, [TABLE_CHANNEL])

    async def test_a_socket_opened_for_no_channel_is_ended(self) -> None:
        websocket = FakeWebSocket(user_data=None)
        await self.routes.lobby_behavior(self.config).open(websocket)
        self.assertIsNotNone(websocket.ended_with)
        self.assertEqual(self.hub.get_watched_channels(), frozenset())

    async def test_closing_a_socket_that_never_opened_changes_nothing(self) -> None:
        websocket = FakeWebSocket(user_data=SocketConnection(channel=TABLE_CHANNEL))
        await self.routes.table_behavior(self.config).close(websocket, NORMAL_CLOSURE, None)
        self.assertEqual(self.source.unsubscribed, [])
