"""
The servicers UNO answers over gRPC.

An app registers these; it builds no binding of its own. Whatever a servicer
needs arrives as an argument, so nothing here reads configuration.
"""

import grpc
from idl.uno.service import game_pb2
from idl.uno.service.game_pb2_grpc import add_UnoServiceServicer_to_server

from product_uno.controller.uno_session_controller import UnoSessionController
from product_uno.service.grpc_uno_service import GrpcUnoService

UNO_SERVICE_NAME = "UnoService"
UNO_SERVICE_DESCRIPTOR = game_pb2.DESCRIPTOR.services_by_name[UNO_SERVICE_NAME]


class ProductUnoServicers:
    """
    One method per service this product answers over gRPC.
    """

    @staticmethod
    def add_uno_service(server: grpc.aio.Server, controller: UnoSessionController) -> str:
        """
        Register the UnoService implementation, and answer its full name.
        """
        add_UnoServiceServicer_to_server(GrpcUnoService(controller=controller), server)
        return UNO_SERVICE_DESCRIPTOR.full_name
