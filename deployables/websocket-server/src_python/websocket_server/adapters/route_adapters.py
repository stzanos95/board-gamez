"""
A socket request and a socket, to what a route needs from them.

No field is read off a request anywhere else.
"""

from websocket_server.service.channel_names import ChannelNames
from websocket_server.service.socket_connection import SocketConnection
from websocket_server.service.socketify_types import SocketifyRequest, SocketifyWebSocket
from websocket_server.service.upgrade_headers import (
    NO_HEADER,
    SEC_WEBSOCKET_EXTENSIONS_HEADER,
    SEC_WEBSOCKET_KEY_HEADER,
    SEC_WEBSOCKET_PROTOCOL_HEADER,
    UpgradeHeaders,
)

TABLE_ID_PARAMETER = 0


class RouteAdapters:
    """
    Every value a route reads, converted to what it is used as.
    """

    @staticmethod
    def table_request_to_channels(request: SocketifyRequest) -> tuple[str, ...] | None:
        """
        The channels of the table the path names, or None when it names none.
        """
        table_id = request.get_parameter(TABLE_ID_PARAMETER)
        if not table_id:
            return None
        return ChannelNames.get_table_channels(table_id)

    @staticmethod
    def request_to_upgrade_headers(request: SocketifyRequest) -> UpgradeHeaders:
        return UpgradeHeaders(
            key=request.get_header(SEC_WEBSOCKET_KEY_HEADER) or NO_HEADER,
            protocol=request.get_header(SEC_WEBSOCKET_PROTOCOL_HEADER) or NO_HEADER,
            extensions=request.get_header(SEC_WEBSOCKET_EXTENSIONS_HEADER) or NO_HEADER,
        )

    @staticmethod
    def websocket_to_connection(websocket: SocketifyWebSocket) -> SocketConnection | None:
        """
        The connection record the upgrade attached, or None when the socket
        carries none.
        """
        data = websocket.get_user_data()
        if not isinstance(data, SocketConnection):
            return None
        return data
