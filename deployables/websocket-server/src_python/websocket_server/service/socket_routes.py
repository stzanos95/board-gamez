"""
The routes a browser opens a socket on, and what each does with it.

A route knows the channels it watches and nothing about what travels on
them. The controller knows the channels and nothing about the paths.
"""

from websocket_server.adapters.route_adapters import RouteAdapters
from websocket_server.controller.subscription_controller import SubscriptionController
from websocket_server.service.channel_names import LOBBY_CHANNEL
from websocket_server.service.socket_connection import SocketConnection
from websocket_server.service.socketify_client import SocketifyClient
from websocket_server.service.socketify_types import (
    SocketifyRequest,
    SocketifyResponse,
    SocketifyWebSocket,
)
from websocket_server.service.websocket_behavior import UpgradeHandler, WebsocketBehavior
from websocket_server.websocket_server_config import ServerConfig

LOBBY_PATH = "/ws/lobby"
TABLE_PATH = "/ws/tables/:table_id"

HTTP_BAD_REQUEST = 400
MISSING_TABLE_ID = "the path names no table"
# RFC 6455 close code for a connection the server will not carry.
POLICY_VIOLATION = 1008
NOT_OPENED_FOR_A_CHANNEL = "the socket was opened for no channel"
LOBBY_CHANNELS = (LOBBY_CHANNEL,)
# The server sends pings itself, so a browser that never writes stays open.
SEND_PINGS_AUTOMATICALLY = True


class SocketRoutes:
    """
    One behavior per route, each attaching the socket to the controller on
    open and detaching it on close.

    A browser sends nothing over these sockets, so there is no message
    handler: a frame that arrives is dropped by the library.
    """

    def __init__(self, controller: SubscriptionController) -> None:
        self._controller = controller

    def lobby_behavior(self, config: ServerConfig) -> WebsocketBehavior:
        """
        `/ws/lobby`: every table's changes.
        """
        return self._behavior(self._upgrade_lobby, config)

    def table_behavior(self, config: ServerConfig) -> WebsocketBehavior:
        """
        `/ws/tables/{table_id}`: one table's changes, and its game's.
        """
        return self._behavior(self._upgrade_table, config)

    def _behavior(self, upgrade: UpgradeHandler, config: ServerConfig) -> WebsocketBehavior:
        return WebsocketBehavior(
            upgrade=upgrade,
            open=self._open,
            close=self._close,
            idle_timeout_seconds=config.idle_timeout_seconds,
            max_payload_bytes=config.max_payload_bytes,
            send_pings_automatically=SEND_PINGS_AUTOMATICALLY,
        )

    def _upgrade_lobby(
        self, response: SocketifyResponse, request: SocketifyRequest, socket_context: object
    ) -> None:
        SocketRoutes._upgrade_to_channels(response, request, socket_context, LOBBY_CHANNELS)

    def _upgrade_table(
        self, response: SocketifyResponse, request: SocketifyRequest, socket_context: object
    ) -> None:
        channels = RouteAdapters.table_request_to_channels(request)
        if channels is None:
            response.write_status(HTTP_BAD_REQUEST).end(MISSING_TABLE_ID)
            return
        SocketRoutes._upgrade_to_channels(response, request, socket_context, channels)

    @staticmethod
    def _upgrade_to_channels(
        response: SocketifyResponse,
        request: SocketifyRequest,
        socket_context: object,
        channels: tuple[str, ...],
    ) -> None:
        headers = RouteAdapters.request_to_upgrade_headers(request)
        response.upgrade(
            headers.key,
            headers.protocol,
            headers.extensions,
            socket_context,
            SocketConnection(channels=channels),
        )

    async def _open(self, websocket: SocketifyWebSocket) -> None:
        connection = RouteAdapters.websocket_to_connection(websocket)
        if connection is None:
            websocket.end(POLICY_VIOLATION, NOT_OPENED_FOR_A_CHANNEL)
            return
        client = SocketifyClient(websocket)
        connection.client = client
        for channel in connection.channels:
            await self._controller.attach(channel, client)

    async def _close(self, websocket: SocketifyWebSocket, code: int, message: bytes | None) -> None:
        connection = RouteAdapters.websocket_to_connection(websocket)
        if connection is None or connection.client is None:
            return
        for channel in connection.channels:
            await self._controller.detach(channel, connection.client)
