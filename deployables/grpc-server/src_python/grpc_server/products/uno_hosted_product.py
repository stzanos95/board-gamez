"""
UNO, as this process hosts it.
"""

import grpc
from game.controller.base_rules import BaseRules
from idl.game.model.game_type_pb2 import GameType
from lobby.controller.base_seating import BaseSeating
from product_uno.controller.uno_rules import UnoRules
from product_uno.controller.uno_seating import UnoSeating
from product_uno.controller.uno_session_controller import UnoSessionController
from product_uno.service.product_uno_servicers import ProductUnoServicers

from grpc_server.platform_controllers import PlatformControllers
from grpc_server.products.base_hosted_product import BaseHostedProduct


class UnoHostedProduct(BaseHostedProduct):
    """
    The rules of UNO, how UNO seats its players, and the service UNO
    answers: UnoService.
    """

    def __init__(self) -> None:
        self._rules = UnoRules()
        self._seating = UnoSeating()

    def get_game_type(self) -> GameType:
        return GameType.GAME_TYPE_UNO

    def get_rules(self) -> BaseRules:
        return self._rules

    def get_seating(self) -> BaseSeating:
        return self._seating

    def add_servicers(
        self, server: grpc.aio.Server, platform: PlatformControllers
    ) -> tuple[str, ...]:
        controller = UnoSessionController(
            tables=platform.tables, seats=platform.seats, sessions=platform.sessions
        )
        return (ProductUnoServicers.add_uno_service(server, controller),)
