"""
What a game must supply for this process to host it.
"""

from abc import ABC, abstractmethod

import grpc
from game.controller.base_rules import BaseRules
from idl.game.model.game_type_pb2 import GameType
from lobby.controller.base_seating import BaseSeating

from grpc_server.platform_controllers import PlatformControllers


class BaseHostedProduct(ABC):
    """
    One game this process hosts: its type, the rules the session controller
    asks, the seating the lobby asks, and the servicers it answers over gRPC.

    The rules and the seating are built when the product is, and the same
    rules object is what `add_servicers` registers, so a call reaching the
    product through this server and a call the session controller makes
    in-process are answered by one implementation.
    """

    @abstractmethod
    def get_game_type(self) -> GameType:
        """
        The game this product hosts.
        """

    @abstractmethod
    def get_rules(self) -> BaseRules:
        """
        The rules the session controller asks for this game.
        """

    @abstractmethod
    def get_seating(self) -> BaseSeating:
        """
        The seating the lobby asks for this game.
        """

    @abstractmethod
    def add_servicers(
        self, server: grpc.aio.Server, platform: PlatformControllers
    ) -> tuple[str, ...]:
        """
        Register every servicer this product answers, and answer their full
        names.
        """
