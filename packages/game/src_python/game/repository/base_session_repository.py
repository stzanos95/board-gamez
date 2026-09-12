"""
The operations any store of sessions must answer.
"""

from abc import ABC, abstractmethod

from google.protobuf.timestamp_pb2 import Timestamp
from idl.game.obj.deadline_pb2 import DeadlineObj
from idl.game.obj.session_pb2 import SessionObj


class BaseSessionRepository(ABC):
    """
    Where sessions are kept, whatever keeps them.

    Reads and writes `SessionObj`, so a caller converts at this boundary. Storage
    only: nothing here decides what a version conflict means, only that the
    versions did not match.

    Every write is guarded by the version the caller read, so a write built on a
    version that has since moved on changes nothing.

    A session's deadline is kept with it: the write that stores a session
    carrying `acts_by` stores its deadline in the same operation, and the write
    that stores one without removes it. Every deadline is therefore at the
    version of the session it belongs to.
    """

    @abstractmethod
    async def upsert(self, session: SessionObj) -> SessionObj | None:
        """
        Write this session and answer it as stored, one version on.

        `metadata.version` is the version the caller read, and 0 says the caller
        believes nothing is stored under this id. None comes back when the
        stored version is a different one, and nothing is written.
        """

    @abstractmethod
    async def read(self, session_id: str) -> SessionObj | None:
        """
        One session, or None when nothing is stored under that id.
        """

    @abstractmethod
    async def list_due_deadline(self, before: Timestamp) -> tuple[DeadlineObj, ...]:
        """
        Every deadline at or before this instant, earliest first.
        """

    @abstractmethod
    async def delete_deadline(self, session_id: str) -> None:
        """
        Remove this session's deadline, if it has one. The session stays.
        """
