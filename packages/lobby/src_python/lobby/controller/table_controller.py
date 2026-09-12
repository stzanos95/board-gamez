"""
What is done to a table.

The one place a lobby decides anything. Everything above it — a servicer, a
router, whatever arrives next — converts and forwards, so a rule lives here or it
lives nowhere.
"""

from core.queue.base_queue_publisher import BaseQueuePublisher
from core.queue.message_utils import QueueMessageUtils
from idl.lobby.model.table_pb2 import Table, TableCollection

from lobby.adapters.event_adapters import EventAdapters
from lobby.adapters.table_adapters import TableAdapters
from lobby.controller.channel_names import LOBBY_CHANNEL, LobbyChannelNames
from lobby.repository.base_table_repository import BaseTableRepository


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

    def __init__(
        self, repository: BaseTableRepository, queue_publisher: BaseQueuePublisher
    ) -> None:
        self._repository = repository
        self._queue_publisher = queue_publisher

    async def upsert_table(self, table: Table) -> Table | None:
        """
        Write a table, creating it if it is not there, and answer it as stored.

        None comes back when the version the table carries is not the stored one,
        and nothing is written.
        """
        stored = await self._repository.upsert(TableAdapters.table_to_table_obj(table))
        return None if stored is None else TableAdapters.table_obj_to_table(stored)

    async def read_table(self, table_id: str) -> Table | None:
        """
        One table, or None when no table has that id.
        """
        stored = await self._repository.read(table_id)
        return None if stored is None else TableAdapters.table_obj_to_table(stored)

    async def delete_table(self, table_id: str, expected_version: int) -> None:
        """
        Retire the table stored under this id at this version.

        Nothing is retired when no table has that id, or when its version is a
        different one. A table that is retired is published as closed, on its
        own channel and on the lobby's.
        """
        if not await self._repository.delete(table_id, expected_version):
            return
        envelope = QueueMessageUtils.pack(EventAdapters.table_id_to_table_closed(table_id))
        await self._queue_publisher.publish(LobbyChannelNames.get_table_channel(table_id), envelope)
        await self._queue_publisher.publish(LOBBY_CHANNEL, envelope)

    async def list_table(self) -> TableCollection:
        """
        Every table.
        """
        return TableAdapters.table_objs_to_table_collection(await self._repository.list_all())
