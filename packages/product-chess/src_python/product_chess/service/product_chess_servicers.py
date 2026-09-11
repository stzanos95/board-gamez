"""
The servicers chess answers over gRPC.

An app registers these; it builds no binding of its own. Whatever a servicer
needs arrives as an argument, so nothing here reads configuration.
"""

import grpc
from idl.chess.service import game_pb2
from idl.chess.service.game_pb2_grpc import add_ChessServiceServicer_to_server
from idl.game.service import rules_pb2
from idl.game.service.rules_pb2_grpc import add_RulesServiceServicer_to_server

from product_chess.controller.chess_rules import ChessRules
from product_chess.controller.chess_session_controller import ChessSessionController
from product_chess.service.grpc_chess_service import GrpcChessService
from product_chess.service.grpc_rules_service import GrpcRulesService

RULES_SERVICE_NAME = "RulesService"
RULES_SERVICE_DESCRIPTOR = rules_pb2.DESCRIPTOR.services_by_name[RULES_SERVICE_NAME]
CHESS_SERVICE_NAME = "ChessService"
CHESS_SERVICE_DESCRIPTOR = game_pb2.DESCRIPTOR.services_by_name[CHESS_SERVICE_NAME]


class ProductChessServicers:
    """
    One method per service this product answers over gRPC.
    """

    @staticmethod
    def add_rules_service(server: grpc.aio.Server, rules: ChessRules) -> str:
        """
        Register the RulesService implementation, and answer its full name.
        """
        add_RulesServiceServicer_to_server(GrpcRulesService(rules=rules), server)
        return RULES_SERVICE_DESCRIPTOR.full_name

    @staticmethod
    def add_chess_service(server: grpc.aio.Server, controller: ChessSessionController) -> str:
        """
        Register the ChessService implementation, and answer its full name.
        """
        add_ChessServiceServicer_to_server(GrpcChessService(controller=controller), server)
        return CHESS_SERVICE_DESCRIPTOR.full_name
