"""
What an upgrade to a socket carries over from the request that asked for it.
"""

from dataclasses import dataclass

SEC_WEBSOCKET_KEY_HEADER = "sec-websocket-key"
SEC_WEBSOCKET_PROTOCOL_HEADER = "sec-websocket-protocol"
SEC_WEBSOCKET_EXTENSIONS_HEADER = "sec-websocket-extensions"
NO_HEADER = ""


@dataclass(frozen=True, slots=True)
class UpgradeHeaders:
    """
    The three handshake headers a socket is upgraded with. A header the
    request did not carry is the empty string.
    """

    key: str
    protocol: str
    extensions: str
