"""
Chess, as this process hosts it.
"""

import grpc
from game.controller.base_rules import BaseRules
from idl.game.model.game_type_pb2 import GameType
from lobby.controller.base_seating import BaseSeating
from product_chess.controller.chess_rules import ChessRules
from product_chess.controller.chess_seating import ChessSeating
from product_chess.controller.chess_session_controller import ChessSessionController
from product_chess.service.product_chess_servicers import ProductChessServicers

from grpc_server.platform_controllers import PlatformControllers
from grpc_server.products.base_hosted_product import BaseHostedProduct


class ChessHostedProduct(BaseHostedProduct):
    """
    The rules of chess, how chess seats its players, and the service chess
    answers: ChessService.
    """

    def __init__(self) -> None:
        self._rules = ChessRules()
        self._seating = ChessSeating()

    def get_game_type(self) -> GameType:
        return GameType.GAME_TYPE_CHESS

    def get_rules(self) -> BaseRules:
        return self._rules

    def get_seating(self) -> BaseSeating:
        return self._seating

    def add_servicers(
        self, server: grpc.aio.Server, platform: PlatformControllers
    ) -> tuple[str, ...]:
        controller = ChessSessionController(
            tables=platform.tables, seats=platform.seats, sessions=platform.sessions
        )
        return (ProductChessServicers.add_chess_service(server, controller),)
