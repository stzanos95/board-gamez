"""
The routers UNO serves over HTTP.

An app includes these; it builds no binding of its own. Whatever a router needs
arrives as an argument, so nothing here reads configuration.
"""

from fastapi import APIRouter
from idl_fastapi.services.uno_service import UnoServiceRouter

from product_uno.service.grpc_uno_client import GrpcUnoClient
from product_uno.service.http_uno_service import HttpUnoService


class ProductUnoRouters:
    """
    One method per service this product answers over HTTP.
    """

    @staticmethod
    def uno_service(client: GrpcUnoClient) -> APIRouter:
        """
        The UnoService paths, declared by the schema and answered over HTTP.
        """
        return UnoServiceRouter.build(HttpUnoService(client=client))
