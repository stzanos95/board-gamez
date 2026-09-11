"""
Where each game's rules answer.

One optional field per game the platform can host. A game whose field is absent
is not served, and a session of that game cannot be created or played.

Adding a game means adding a field here and an entry in `rules_client_provider`.
Nothing existing changes.
"""

from dataclasses import dataclass

from idl.game.model.game_type_pb2 import GameType
from mashumaro.mixins.yaml import DataClassYAMLMixin


@dataclass(frozen=True, slots=True)
class RulesUpstreamConfig(DataClassYAMLMixin):
    """
    Where one game's rules answer, and what a call to them may carry.

    Plain HTTP/2 without TLS: a rules service is reachable only from inside.

    The message limits are the caller's half of a pair. A server that accepts
    more than a client will receive fails on whichever side is smaller, so these
    are set together with the limits the rules service itself is configured
    with.
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
class RulesConfig(DataClassYAMLMixin):
    """
    The rules of every game this platform hosts, one field per game.
    """

    chess: RulesUpstreamConfig | None = None


RulesUpstreamsByGameType = dict[GameType, RulesUpstreamConfig | None]
