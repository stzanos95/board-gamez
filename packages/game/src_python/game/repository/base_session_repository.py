"""
The operations any store of sessions must answer.
"""

from abc import ABC, abstractmethod

from idl.game.obj.session_pb2 import SessionObj


class BaseSessionRepository(ABC):
    """
    Where sessions are kept, whatever keeps them.

    Reads and writes `SessionObj`, so a caller converts at this boundary. Storage
    only: nothing here decides what a version conflict means, only that the
    versions did not match.

    Every write is guarded by the version the caller read, so a write built on a
    version that has since moved on changes nothing.
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
