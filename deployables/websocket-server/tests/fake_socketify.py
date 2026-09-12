"""
The socketify objects a route touches, faked so a route test needs no socket.
"""

from dataclasses import dataclass, field

ParametersByIndex = dict[int, str]
HeadersByName = dict[str, str]


class FakeRequest:
    """
    A request answering the parameters and headers it was given.
    """

    def __init__(self, parameters: ParametersByIndex, headers: HeadersByName) -> None:
        self._parameters = parameters
        self._headers = headers

    def get_parameter(self, index: int) -> str | None:
        return self._parameters.get(index)

    def get_header(self, lower_case_header: str) -> str | None:
        return self._headers.get(lower_case_header)


@dataclass(slots=True)
class FakeResponse:
    """
    Records the upgrade it was asked for, or the status it was ended with.

    Mutable: it is written by the code under test and read by the test.
    """

    upgraded_with: object = None
    key: str = ""
    protocol: str = ""
    extensions: str = ""
    status: int | None = None
    ended_with: str | None = None

    def upgrade(
        self,
        sec_web_socket_key: str,
        sec_web_socket_protocol: str,
        sec_web_socket_extensions: str,
        socket_context: object,
        user_data: object,
    ) -> bool:
        self.key = sec_web_socket_key
        self.protocol = sec_web_socket_protocol
        self.extensions = sec_web_socket_extensions
        self.upgraded_with = user_data
        return True

    def write_status(self, status: int) -> "FakeResponse":
        self.status = status
        return self

    def end(self, message: str) -> object:
        self.ended_with = message
        return self


@dataclass(slots=True)
class FakeWebSocket:
    """
    A socket carrying the user data an upgrade attached, recording what it is
    sent and whether it was ended.

    Mutable: it is written by the code under test and read by the test.
    """

    user_data: object
    sent: list[bytes] = field(default_factory=list)
    ended_with: int | None = None

    def send(self, message: bytes, opcode: int) -> object:
        self.sent.append(message)
        return True

    def end(self, code: int, message: str) -> object:
        self.ended_with = code
        return self

    def get_user_data(self) -> object:
        return self.user_data
