"""
The operations any store of tables must answer.
"""

from abc import ABC, abstractmethod

from idl.lobby.obj.table_pb2 import TableObj


class BaseTableRepository(ABC):
    """
    Where tables are kept, whatever keeps them.

    Reads and writes `TableObj`, so a caller converts at this boundary. Storage
    only: nothing here decides what a version conflict means, only that the
    versions did not match.

    Every write is guarded by the version the caller read, so a write built on a
    version that has since moved on changes nothing.
    """

    @abstractmethod
    async def upsert(self, table: TableObj) -> TableObj | None:
        """
        Write this table and answer it as stored, one version on.

        `metadata.version` is the version the caller read, and 0 says the caller
        believes nothing is stored under this id. None comes back when the
        stored version is a different one, and nothing is written.
        """

    @abstractmethod
    async def read(self, table_id: str) -> TableObj | None:
        """
        One table, or None when nothing is stored under that id.
        """

    @abstractmethod
    async def delete(self, table_id: str, expected_version: int) -> bool:
        """
        Remove the table stored under this id at this version, and answer
        whether one was removed.

        Nothing is removed when nothing is stored under the id, or when the
        stored version is a different one.
        """

    @abstractmethod
    async def list_all(self) -> tuple[TableObj, ...]:
        """
        Every table currently stored.
        """
