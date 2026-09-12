"""
The routers a lobby serves over HTTP.

An app includes these; it builds no binding of its own. Whatever a router needs
arrives as an argument, so nothing here reads configuration.
"""

from fastapi import APIRouter
from idl_fastapi.services.seat_service import SeatServiceRouter
from idl_fastapi.services.table_service import TableServiceRouter

from lobby.service.grpc_seat_client import GrpcSeatClient
from lobby.service.grpc_table_client import GrpcTableClient
from lobby.service.http_seat_service import HttpSeatService
from lobby.service.http_table_service import HttpTableService


class LobbyRouters:
    """
    One method per service this domain answers over HTTP.
    """

    @staticmethod
    def table_service(client: GrpcTableClient) -> APIRouter:
        """
        The TableService paths, declared by the schema and answered over HTTP.

        The client is the one this domain calls to do the work; it is handed in
        so that its channel belongs to whoever runs the process.
        """
        return TableServiceRouter.build(HttpTableService(client=client))

    @staticmethod
    def seat_service(client: GrpcSeatClient) -> APIRouter:
        """
        The SeatService paths, declared by the schema and answered over HTTP.
        """
        return SeatServiceRouter.build(HttpSeatService(client=client))
