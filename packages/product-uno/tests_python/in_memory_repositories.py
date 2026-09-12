"""
Stores that keep their rows in a dictionary, so a controller test needs no
running Redis. Each guards the version the way its base class says.
"""

from core.protobuf.message_utils import ProtobufMessageUtils
from game.repository.base_session_repository import BaseSessionRepository
from google.protobuf.timestamp_pb2 import Timestamp
from idl.game.obj.deadline_pb2 import DeadlineObj
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
        self._removed_deadlines: set[str] = set()

    async def upsert(self, session: SessionObj) -> SessionObj | None:
        stored = self._sessions.get(session.metadata.id)
        stored_version = ABSENT_VERSION if stored is None else stored.metadata.version
        if session.metadata.version != stored_version:
            return None
        written = ProtobufMessageUtils.copy_of_message(session)
        written.metadata.version = session.metadata.version + VERSION_INCREMENT
        self._sessions[session.metadata.id] = written
        self._removed_deadlines.discard(session.metadata.id)
        return written

    async def read(self, session_id: str) -> SessionObj | None:
        return self._sessions.get(session_id)

    async def list_due_deadline(self, before: Timestamp) -> tuple[DeadlineObj, ...]:
        due = [
            DeadlineObj(metadata=stored.metadata, acts_by=stored.acts_by)
            for stored in self._sessions.values()
            if stored.HasField("acts_by")
            and stored.acts_by.ToDatetime() <= before.ToDatetime()
            and stored.metadata.id not in self._removed_deadlines
        ]
        due.sort(key=lambda deadline: deadline.acts_by.ToDatetime())
        return tuple(due)

    async def delete_deadline(self, session_id: str) -> None:
        self._removed_deadlines.add(session_id)


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

    async def delete(self, table_id: str, expected_version: int) -> bool:
        stored = self._tables.get(table_id)
        if stored is None or stored.metadata.version != expected_version:
            return False
        del self._tables[table_id]
        return True

    async def list_all(self) -> tuple[TableObj, ...]:
        return tuple(self._tables.values())
