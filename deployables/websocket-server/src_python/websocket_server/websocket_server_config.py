"""
The socket server's settings, parsed from YAML.

Every value the app needs to run is a field here, and nothing in the app reads
the environment.

mashumaro reads these annotations at runtime to build the parser, so
`from __future__ import annotations` would leave it nothing to read.
"""

from dataclasses import dataclass

from core.queue.config import QueueConfig
from mashumaro.mixins.yaml import DataClassYAMLMixin

from websocket_server.log_level import LogLevel


@dataclass(frozen=True, slots=True)
class ApplicationConfig(DataClassYAMLMixin):
    """
    What the application calls itself.
    """

    name: str
    version: str


@dataclass(frozen=True, slots=True)
class ServerConfig(DataClassYAMLMixin):
    """
    The socket the server listens on, how it logs, and what a connection may do.

    The listener speaks plain HTTP; TLS is terminated ahead of this process.

    A connection that has carried nothing for `idle_timeout_seconds` is closed,
    and 0 disables that. The server pings on its own, so a browser that is
    still connected is not closed for sending nothing. A frame larger than
    `max_payload_bytes` is refused.
    """

    host: str
    port: int
    log_level: LogLevel
    idle_timeout_seconds: int
    max_payload_bytes: int


@dataclass(frozen=True, slots=True)
class WebsocketServerConfig(DataClassYAMLMixin):
    """
    Everything the socket server needs to start.

    `sources` is where events arrive from. Every source is consumed, and every
    source is subscribed to a channel while a socket watches it. At least one
    is required.
    """

    application: ApplicationConfig
    server: ServerConfig
    sources: list[QueueConfig]
