"""
The server's settings, parsed from YAML.

Every value the app needs to run is a field here, and nothing in the app reads
the environment.

mashumaro reads these annotations at runtime to build the parser, so
`from __future__ import annotations` would leave it nothing to read.
"""

from dataclasses import dataclass

from mashumaro.mixins.yaml import DataClassYAMLMixin

from grpc_server.log_level import LogLevel


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
    The socket the server listens on, what it will carry, and how it stops.

    The listener speaks plain HTTP/2 without TLS; transport security is
    terminated ahead of this process, which is only reachable from inside.

    `graceful_shutdown_seconds` is how long a call already in flight has to
    finish once the process has been asked to stop. Calls still running when it
    elapses are cancelled.
    """

    host: str
    port: int
    log_level: LogLevel
    maximum_concurrent_rpcs: int
    max_receive_message_bytes: int
    max_send_message_bytes: int
    graceful_shutdown_seconds: int
    reflection: bool


@dataclass(frozen=True, slots=True)
class ServiceHostConfig(DataClassYAMLMixin):
    """
    Everything the server needs to start.
    """

    application: ApplicationConfig
    server: ServerConfig
