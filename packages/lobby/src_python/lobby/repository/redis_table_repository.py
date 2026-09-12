"""
Tables kept in Redis.
"""

from core.protobuf.message_utils import ProtobufMessageUtils
from idl.lobby.obj.table_pb2 import TableObj
from redis.asyncio import Redis

from lobby.repository.base_table_repository import BaseTableRepository
from lobby.repository.config import RedisTableRepositoryConfig
from lobby.repository.redis_table_row import DATA_FIELD, VERSION_FIELD, RedisTableRow

# Both scripts compare the stored version before writing anything, so a caller
# working from a version that has since moved on writes nothing. A missing hash
# reads as version 0, which is the version a caller carries when it believes it
# is creating.
UPSERT_TABLE_SCRIPT = f"""
local stored = redis.call('HGET', KEYS[1], '{VERSION_FIELD}')
if (stored or '0') ~= ARGV[1] then return 0 end
redis.call('HSET', KEYS[1], '{VERSION_FIELD}', ARGV[2], '{DATA_FIELD}', ARGV[3])
return 1
"""

DELETE_TABLE_SCRIPT = f"""
if redis.call('HGET', KEYS[1], '{VERSION_FIELD}') ~= ARGV[1] then return 0 end
return redis.call('DEL', KEYS[1])
"""

SCRIPT_APPLIED = 1
VERSION_INCREMENT = 1


class RedisTableRepository(BaseTableRepository):
    """
    Every table operation, against one Redis instance.

    Holds its own client, built from the settings it is given. Responses are left
    undecoded, because a table is written as bytes.
    """

    def __init__(self, config: RedisTableRepositoryConfig) -> None:
        self._key_prefix = config.key_prefix
        self._client = Redis(host=config.host, port=config.port, db=config.database)
        self._upsert_table = self._client.register_script(UPSERT_TABLE_SCRIPT)
        self._delete_table = self._client.register_script(DELETE_TABLE_SCRIPT)

    async def upsert(self, table: TableObj) -> TableObj | None:
        written = ProtobufMessageUtils.copy_of_message(table)
        written.metadata.version = table.metadata.version + VERSION_INCREMENT
        applied = await self._upsert_table(
            keys=[RedisTableRow.table_key(self._key_prefix, table.metadata.id)],
            args=[
                str(table.metadata.version),
                str(written.metadata.version),
                RedisTableRow.encode_table(written),
            ],
        )
        return written if applied == SCRIPT_APPLIED else None

    async def read(self, table_id: str) -> TableObj | None:
        data = await self._client.hget(
            RedisTableRow.table_key(self._key_prefix, table_id), DATA_FIELD
        )
        return None if data is None else RedisTableRow.decode_table(data)

    async def delete(self, table_id: str, expected_version: int) -> bool:
        removed = await self._delete_table(
            keys=[RedisTableRow.table_key(self._key_prefix, table_id)],
            args=[str(expected_version)],
        )
        return bool(removed == SCRIPT_APPLIED)

    async def list_all(self) -> tuple[TableObj, ...]:
        tables = []
        async for key in self._client.scan_iter(
            match=RedisTableRow.every_table_key(self._key_prefix)
        ):
            data = await self._client.hget(key, DATA_FIELD)
            if data is not None:
                tables.append(RedisTableRow.decode_table(data))
        return tuple(tables)
