"""
The mapping socketify takes for a socket route.

Models the shape the library wants, so its keys are named once, here, and the
conversion to a mapping happens in one place.
"""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from websocket_server.service.socketify_types import (
    SocketifyRequest,
    SocketifyResponse,
    SocketifyWebSocket,
)

UPGRADE_KEY = "upgrade"
OPEN_KEY = "open"
CLOSE_KEY = "close"
IDLE_TIMEOUT_KEY = "idle_timeout"
MAX_PAYLOAD_LENGTH_KEY = "max_payload_length"
SEND_PINGS_AUTOMATICALLY_KEY = "send_pings_automatically"

UpgradeHandler = Callable[[SocketifyResponse, SocketifyRequest, object], None]
OpenHandler = Callable[[SocketifyWebSocket], Awaitable[None]]
CloseHandler = Callable[[SocketifyWebSocket, int, bytes | None], Awaitable[None]]


@dataclass(frozen=True, slots=True)
class WebsocketBehavior:
    """
    What a route does at each point in a socket's life, and the limits it
    keeps.

    `idle_timeout_seconds` is 0 or at least 8; the library refuses anything
    between. With `send_pings_automatically` the server keeps an idle socket
    open on its own.
    """

    upgrade: UpgradeHandler
    open: OpenHandler
    close: CloseHandler
    idle_timeout_seconds: int
    max_payload_bytes: int
    send_pings_automatically: bool

    def to_dict(self) -> dict[str, object]:
        """
        The mapping socketify takes. The keys are the library's.
        """
        return {
            UPGRADE_KEY: self.upgrade,
            OPEN_KEY: self.open,
            CLOSE_KEY: self.close,
            IDLE_TIMEOUT_KEY: self.idle_timeout_seconds,
            MAX_PAYLOAD_LENGTH_KEY: self.max_payload_bytes,
            SEND_PINGS_AUTOMATICALLY_KEY: self.send_pings_automatically,
        }
