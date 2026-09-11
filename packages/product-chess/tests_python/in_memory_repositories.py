"""
Stores that keep their rows in a dictionary, so a controller test needs no
running Redis. Each guards the version the way its base class says.
"""

from core.protobuf.message_utils import ProtobufMessageUtils
from game.repository.base_session_repository import BaseSessionRepository
from idl.game.obj.session_pb2 import SessionObj
from idl.lobby.obj.table_pb2 import TableObj
from lobby.repository.base_table_repository import BaseTableRepository

VERSION_INCREMENT = 1
ABSENT_VERSION = 0

SessionObjsById = dict[str, SessionObj]
TableObjsById = dict[str, TableObj]


class InMemorySessionRepository(BaseSessionRepository):
    """
    Every session operation, against a dictionary keyed by session id.
    """

    def __init__(self) -> None:
        self._sessions: SessionObjsById = {}

    async def upsert(self, session: SessionObj) -> SessionObj | None:
        stored = self._sessions.get(session.metadata.id)
        stored_version = ABSENT_VERSION if stored is None else stored.metadata.version
        if session.metadata.version != stored_version:
            return None
        written = ProtobufMessageUtils.copy_of_message(session)
        written.metadata.version = session.metadata.version + VERSION_INCREMENT
        self._sessions[session.metadata.id] = written
        return written

    async def read(self, session_id: str) -> SessionObj | None:
        return self._sessions.get(session_id)


class InMemoryTableRepository(BaseTableRepository):
    """
    Every table operation, against a dictionary keyed by table id.
    """

    def __init__(self) -> None:
        self._tables: TableObjsById = {}

    async def upsert(self, table: TableObj) -> TableObj | None:
        stored = self._tables.get(table.metadata.id)
        stored_version = ABSENT_VERSION if stored is None else stored.metadata.version
        if table.metadata.version != stored_version:
            return None
        written = ProtobufMessageUtils.copy_of_message(table)
        written.metadata.version = table.metadata.version + VERSION_INCREMENT
        self._tables[table.metadata.id] = written
        return written

    async def read(self, table_id: str) -> TableObj | None:
        return self._tables.get(table_id)

    async def delete(self, table_id: str, expected_version: int) -> None:
        stored = self._tables.get(table_id)
        if stored is not None and stored.metadata.version == expected_version:
            del self._tables[table_id]

    async def list_all(self) -> tuple[TableObj, ...]:
        return tuple(self._tables.values())
