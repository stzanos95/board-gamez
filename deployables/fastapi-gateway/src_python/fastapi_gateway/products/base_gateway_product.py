"""
What a game must supply for this gateway to serve it.
"""

from abc import ABC, abstractmethod

from core.grpc.channel_options import ChannelOptions
from fastapi import APIRouter
from google.protobuf.descriptor import FileDescriptor


class BaseGatewayProduct(ABC):
    """
    One game this gateway serves: the client it calls the platform through,
    the router it answers over HTTP, and the files declaring every type the
    game packs into a payload.

    A payload crosses the platform's paths as `google.protobuf.Any`, and
    translating one between JSON and a message resolves its `@type` against
    the types this process has imported. A type not declared by one of the
    files answered here cannot be sent or answered as JSON.
    """

    @abstractmethod
    async def connect(self, address: str, options: ChannelOptions) -> None:
        """
        Dial the platform with every client this product holds.
        """

    @abstractmethod
    async def close(self) -> None:
        """
        Close every channel this product opened.
        """

    @abstractmethod
    def get_router(self) -> APIRouter:
        """
        The paths this product answers over HTTP.
        """

    @abstractmethod
    def get_payload_files(self) -> tuple[FileDescriptor, ...]:
        """
        The schema files declaring every type this product packs into a payload.
        """
