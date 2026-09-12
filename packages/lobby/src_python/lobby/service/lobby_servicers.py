"""
The servicers a lobby answers over gRPC.

An app registers these; it builds no binding of its own. Whatever a servicer
needs arrives as an argument, so nothing here reads configuration.
"""

import grpc
from idl.lobby.service import seat_pb2, table_pb2
from idl.lobby.service.seat_pb2_grpc import add_SeatServiceServicer_to_server
from idl.lobby.service.table_pb2_grpc import add_TableServiceServicer_to_server

from lobby.controller.seat_controller import SeatController
from lobby.controller.table_controller import TableController
from lobby.service.grpc_seat_service import GrpcSeatService
from lobby.service.grpc_table_service import GrpcTableService

TABLE_SERVICE_NAME = "TableService"
TABLE_SERVICE_DESCRIPTOR = table_pb2.DESCRIPTOR.services_by_name[TABLE_SERVICE_NAME]
SEAT_SERVICE_NAME = "SeatService"
SEAT_SERVICE_DESCRIPTOR = seat_pb2.DESCRIPTOR.services_by_name[SEAT_SERVICE_NAME]


class LobbyServicers:
    """
    One method per service this domain answers over gRPC.
    """

    @staticmethod
    def add_table_service(server: grpc.aio.Server, controller: TableController) -> str:
        """
        Register the TableService implementation, and answer its full name.

        The controller is what does the work; it is handed in so that whatever it
        depends on is built where the process is configured.

        Registration mutates the server, which is what gRPC offers in place of
        the router an HTTP framework returns. The name comes back so a caller can
        publish it for reflection without spelling it out a second time.
        """
        add_TableServiceServicer_to_server(GrpcTableService(controller=controller), server)
        return TABLE_SERVICE_DESCRIPTOR.full_name

    @staticmethod
    def add_seat_service(server: grpc.aio.Server, controller: SeatController) -> str:
        """
        Register the SeatService implementation, and answer its full name.
        """
        add_SeatServiceServicer_to_server(GrpcSeatService(controller=controller), server)
        return SEAT_SERVICE_DESCRIPTOR.full_name
