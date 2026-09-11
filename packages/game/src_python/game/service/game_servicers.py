"""
The servicers the game domain answers over gRPC.

An app registers these; it builds no binding of its own. Whatever a servicer
needs arrives as an argument, so nothing here reads configuration.
"""

import grpc
from idl.game.service import game_spec_pb2, session_pb2
from idl.game.service.game_spec_pb2_grpc import add_GameSpecServiceServicer_to_server
from idl.game.service.session_pb2_grpc import add_SessionServiceServicer_to_server

from game.controller.game_spec_controller import GameSpecController
from game.controller.session_controller import SessionController
from game.service.grpc_game_spec_service import GrpcGameSpecService
from game.service.grpc_session_service import GrpcSessionService

SESSION_SERVICE_NAME = "SessionService"
SESSION_SERVICE_DESCRIPTOR = session_pb2.DESCRIPTOR.services_by_name[SESSION_SERVICE_NAME]
GAME_SPEC_SERVICE_NAME = "GameSpecService"
GAME_SPEC_SERVICE_DESCRIPTOR = game_spec_pb2.DESCRIPTOR.services_by_name[GAME_SPEC_SERVICE_NAME]


class GameServicers:
    """
    One method per service this domain answers over gRPC.
    """

    @staticmethod
    def add_session_service(server: grpc.aio.Server, controller: SessionController) -> str:
        """
        Register the SessionService implementation, and answer its full name.
        """
        add_SessionServiceServicer_to_server(GrpcSessionService(controller=controller), server)
        return SESSION_SERVICE_DESCRIPTOR.full_name

    @staticmethod
    def add_game_spec_service(server: grpc.aio.Server, controller: GameSpecController) -> str:
        """
        Register the GameSpecService implementation, and answer its full name.
        """
        add_GameSpecServiceServicer_to_server(GrpcGameSpecService(controller=controller), server)
        return GAME_SPEC_SERVICE_DESCRIPTOR.full_name
