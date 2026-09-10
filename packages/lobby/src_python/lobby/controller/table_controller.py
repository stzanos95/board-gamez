"""
What is done to a table.

The one place a lobby decides anything. Everything above it — a servicer, a
router, whatever arrives next — converts and forwards, so a rule lives here or it
lives nowhere.
"""

from idl.lobby.model.table_pb2 import Table


class TableController:
    """
    Every operation a table has, and the collaborators they need.

    Takes and answers with the domain's own types. A request is the shape one
    transport carries an argument in, and unpacking it belongs to whatever
    received it, so nothing from `idl.lobby.dto` reaches this far.

    Built once at the entry point and passed to whatever serves it, so what a
    controller talks to is chosen where the process is configured and never
    reached for part-way down a call.
    """

    def __init__(self) -> None:
        """
        Nothing is needed yet.

        The store a table is read from and written to arrives here as an
        argument, along with anything else this comes to depend on.
        """

    async def upsert_table(self, table: Table) -> Table:
        """
        Write a table, creating it if it is not there, and answer it as stored.

        Refuses a table whose version is earlier than the stored one.
        """
        raise NotImplementedError

    async def read_table(self, table_id: str) -> Table | None:
        """
        One table, or None when no table has that id.
        """
        raise NotImplementedError

    async def delete_table(self, table_id: str, expected_version: int) -> None:
        """
        Retire a table, refusing a version earlier than the stored one.
        """
        raise NotImplementedError

    async def list_table(self) -> tuple[Table, ...]:
        """
        Every table.
        """
        raise NotImplementedError
