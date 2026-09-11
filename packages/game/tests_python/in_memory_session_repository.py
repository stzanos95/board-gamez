"""
A session store that keeps its sessions in a dictionary.

Answers exactly what the base class says it will, so a controller test does not
need a running Redis. It guards the version the same way.
"""

from core.protobuf.message_utils import ProtobufMessageUtils
from idl.game.obj.session_pb2 import SessionObj

from game.repository.base_session_repository import BaseSessionRepository

VERSION_INCREMENT = 1
ABSENT_VERSION = 0

SessionObjsById = dict[str, SessionObj]


class InMemorySessionRepository(BaseSessionRepository):
    """
    Every session operation, against a dictionary keyed by session id.
    """

    def __init__(self) -> None:
        self._sessions: SessionObjsById = {}

    async def upsert(self, session: SessionObj) -> SessionObj | None:
        if session.metadata.version != self._version_of(session.metadata.id):
            return None
        written = ProtobufMessageUtils.copy_of_message(session)
        written.metadata.version = session.metadata.version + VERSION_INCREMENT
        self._sessions[session.metadata.id] = written
        return written

    async def read(self, session_id: str) -> SessionObj | None:
        return self._sessions.get(session_id)

    def _version_of(self, session_id: str) -> int:
        stored = self._sessions.get(session_id)
        return ABSENT_VERSION if stored is None else stored.metadata.version


class RefusingOnceSessionRepository(InMemorySessionRepository):
    """
    A store whose next write is refused, as if another writer had moved the
    version between a caller's read and its write.
    """

    def __init__(self) -> None:
        super().__init__()
        self.refuse_next_write = False

    async def upsert(self, session: SessionObj) -> SessionObj | None:
        if self.refuse_next_write:
            self.refuse_next_write = False
            return None
        return await super().upsert(session)
