"""
The routers a lobby serves over HTTP.

An app includes these; it builds no binding of its own. Whatever a router needs
arrives as an argument, so nothing here reads configuration.
"""

from fastapi import APIRouter
from idl_fastapi.services.table_service import TableServiceRouter

from lobby.service.http_table_service import HttpTableService


class LobbyRouters:
    """
    One method per service this domain answers over HTTP.
    """

    @staticmethod
    def table_service() -> APIRouter:
        """
        The TableService paths, declared by the schema and answered over HTTP.
        """
        return TableServiceRouter.build(HttpTableService())
