import unittest

from fastapi.routing import APIRoute

from lobby.service.lobby_routers import LobbyRouters

TABLE_SERVICE_PATHS = {
    "/internal/platform/lobby/upsert/table",
    "/internal/platform/lobby/read/table",
    "/internal/platform/lobby/delete/table",
    "/internal/platform/lobby/list/table",
}


class TableServiceRouterTest(unittest.TestCase):
    def test_every_path_the_schema_declares_is_routed(self) -> None:
        router = LobbyRouters.table_service()
        paths = {route.path for route in router.routes if isinstance(route, APIRoute)}
        self.assertEqual(paths, TABLE_SERVICE_PATHS)
