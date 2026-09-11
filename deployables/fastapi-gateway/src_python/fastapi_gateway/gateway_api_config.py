"""
The gateway's settings, parsed from YAML.

Every value the app needs to run is a field here, and nothing in the app reads
the environment.

mashumaro reads these annotations at runtime to build the parser, so
`from __future__ import annotations` would leave it nothing to read.
"""

from dataclasses import dataclass

from mashumaro.mixins.yaml import DataClassYAMLMixin

from fastapi_gateway.log_level import LogLevel


@dataclass(frozen=True, slots=True)
class ApplicationConfig(DataClassYAMLMixin):
    """
    What the application calls itself, and where it is mounted.

    `root_path` is the path prefix stripped before a request reaches this
    process. It is empty when the gateway is served at the root.
    """

    title: str
    version: str
    root_path: str


@dataclass(frozen=True, slots=True)
class ServerConfig(DataClassYAMLMixin):
    """
    The socket the gateway listens on, and how it logs.

    The listener speaks plain HTTP; TLS is terminated ahead of this process. The
    scheme and client address of the original request therefore arrive in
    forwarded headers, and are read only when `proxy_headers` is true and only
    from the addresses `forwarded_allow_ips` names.
    """

    host: str
    port: int
    log_level: LogLevel
    access_log: bool
    proxy_headers: bool
    forwarded_allow_ips: str


@dataclass(frozen=True, slots=True)
class GrpcConfig(DataClassYAMLMixin):
    """
    Where the internal gRPC server answers, and what a call to it may carry.

    Plain HTTP/2 without TLS: it is reachable only from inside.

    The message limits are the caller's half of a pair. A server that accepts
    more than a client will receive fails on whichever side is smaller, so these
    are set together with the limits the service itself is configured with.
    """

    hostname: str
    port: int
    max_receive_message_bytes: int
    max_send_message_bytes: int

    @property
    def address(self) -> str:
        """
        The endpoint gRPC dials.
        """
        return f"{self.hostname}:{self.port}"


@dataclass(frozen=True, slots=True)
class GatewayAPIConfig(DataClassYAMLMixin):
    """
    Everything the gateway needs to start.
    """

    application: ApplicationConfig
    server: ServerConfig
    grpc: GrpcConfig
