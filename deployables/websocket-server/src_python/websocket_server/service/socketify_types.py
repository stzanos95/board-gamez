"""
The surface of socketify this server uses, as protocols.

socketify ships no type information. These name what each object answers, so
every handler is typed against them and nothing else in this server reaches
for an attribute the library does not declare here.
"""

from typing import Protocol


class SocketifyRequest(Protocol):
    """
    The request a socket is opened with, read during the upgrade.
    """

    def get_parameter(self, index: int) -> str | None:
        """
        The path parameter at this position, or None when the path has none.
        """

    def get_header(self, lower_case_header: str) -> str | None:
        """
        The header of this name, or None when the request carries none.
        """


class SocketifyResponse(Protocol):
    """
    The response an upgrade is answered on.
    """

    def upgrade(
        self,
        sec_web_socket_key: str,
        sec_web_socket_protocol: str,
        sec_web_socket_extensions: str,
        socket_context: object,
        user_data: object,
    ) -> bool:
        """
        Turn the connection into a socket. `user_data` is what the socket's
        `get_user_data` answers for the rest of its life.
        """

    def write_status(self, status: int) -> "SocketifyResponse":
        """
        Set the status of the response.
        """

    def end(self, message: str) -> object:
        """
        Send the response and close it.
        """


class SocketifyWebSocket(Protocol):
    """
    One open socket.
    """

    def send(self, message: bytes, opcode: int) -> object:
        """
        Send one frame.
        """

    def end(self, code: int, message: str) -> object:
        """
        Close the socket with this code and reason.
        """

    def get_user_data(self) -> object:
        """
        What the upgrade attached to this socket.
        """
