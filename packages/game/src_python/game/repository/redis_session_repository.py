"""
Sessions kept in Redis.
"""

from core.protobuf.message_utils import ProtobufMessageUtils
from idl.game.obj.session_pb2 import SessionObj
from redis.asyncio import Redis

from game.repository.base_session_repository import BaseSessionRepository
from game.repository.config import RedisSessionRepositoryConfig
from game.repository.redis_session_row import DATA_FIELD, VERSION_FIELD, RedisSessionRow

# The script compares the stored version before writing anything, so a caller
# working from a version that has since moved on writes nothing. A missing hash
# reads as version 0, which is the version a caller carries when it believes it
# is creating.
UPSERT_SESSION_SCRIPT = f"""
local stored = redis.call('HGET', KEYS[1], '{VERSION_FIELD}')
if (stored or '0') ~= ARGV[1] then return 0 end
redis.call('HSET', KEYS[1], '{VERSION_FIELD}', ARGV[2], '{DATA_FIELD}', ARGV[3])
return 1
"""

SCRIPT_APPLIED = 1
VERSION_INCREMENT = 1


class RedisSessionRepository(BaseSessionRepository):
    """
    Every session operation, against one Redis instance.

    Holds its own client, built from the settings it is given. Responses are left
    undecoded, because a session is written as bytes.
    """

    def __init__(self, config: RedisSessionRepositoryConfig) -> None:
        self._key_prefix = config.key_prefix
        self._client = Redis(host=config.host, port=config.port, db=config.database)
        self._upsert_session = self._client.register_script(UPSERT_SESSION_SCRIPT)

    async def upsert(self, session: SessionObj) -> SessionObj | None:
        written = ProtobufMessageUtils.copy_of_message(session)
        written.metadata.version = session.metadata.version + VERSION_INCREMENT
        applied = await self._upsert_session(
            keys=[RedisSessionRow.session_key(self._key_prefix, session.metadata.id)],
            args=[
                str(session.metadata.version),
                str(written.metadata.version),
                RedisSessionRow.encode_session(written),
            ],
        )
        return written if applied == SCRIPT_APPLIED else None

    async def read(self, session_id: str) -> SessionObj | None:
        data = await self._client.hget(
            RedisSessionRow.session_key(self._key_prefix, session_id), DATA_FIELD
        )
        return None if data is None else RedisSessionRow.decode_session(data)
