"""
A table store that keeps its tables in a dictionary.

Answers exactly what the base class says it will, so a controller test does not
need a running Redis. It guards the version the same way.
"""

from core.protobuf.message_utils import ProtobufMessageUtils
from idl.lobby.obj.table_pb2 import TableObj

from lobby.repository.base_table_repository import BaseTableRepository

VERSION_INCREMENT = 1
ABSENT_VERSION = 0


class InMemoryTableRepository(BaseTableRepository):
    """
    Every table operation, against a dictionary keyed by table id.
    """

    def __init__(self) -> None:
        # Keys are data — a table id names the table stored under it.
        self._tables: dict[str, TableObj] = {}

    async def upsert(self, table: TableObj) -> TableObj | None:
        if table.metadata.version != self._version_of(table.metadata.id):
            return None
        written = ProtobufMessageUtils.copy_of_message(table)
        written.metadata.version = table.metadata.version + VERSION_INCREMENT
        self._tables[table.metadata.id] = written
        return written

    async def read(self, table_id: str) -> TableObj | None:
        return self._tables.get(table_id)

    async def delete(self, table_id: str, expected_version: int) -> bool:
        if table_id not in self._tables or expected_version != self._version_of(table_id):
            return False
        del self._tables[table_id]
        return True

    async def list_all(self) -> tuple[TableObj, ...]:
        return tuple(self._tables.values())

    def _version_of(self, table_id: str) -> int:
        stored = self._tables.get(table_id)
        return ABSENT_VERSION if stored is None else stored.metadata.version
