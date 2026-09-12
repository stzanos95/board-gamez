"""
The keys and fields one session occupies in Redis, and the index its deadline
sits in.

A session is a hash of two fields: the version as decimal text, and the session
in protobuf's binary wire format. The version is readable without decoding the
session, which is what lets a compare-and-set run inside Redis.

Every deadline is one entry in a sorted set shared by the deployment, the
session id scored by the instant it runs out, so the ones that have passed are
read as a range.
"""

from dataclasses import dataclass

from core.protobuf.message_utils import ProtobufMessageUtils
from google.protobuf.timestamp_pb2 import Timestamp
from idl.core.obj.object_metadata_pb2 import ObjectMetadata
from idl.game.obj.deadline_pb2 import DeadlineObj
from idl.game.obj.session_pb2 import SessionObj

VERSION_FIELD = "version"
DATA_FIELD = "data"

KEY_SEPARATOR = ":"
SESSION_KEY_SEGMENT = "session"
DEADLINE_INDEX_KEY_SEGMENT = "deadline"
SESSION_ENCODING = "utf-8"
NO_DEADLINE_SCORE = ""
RANGE_ITEM_LENGTH = 2


@dataclass(frozen=True, slots=True)
class DeadlineIndexEntry:
    """
    One entry of the deadline index: the session it names, and the instant it
    is scored by, in whole milliseconds.
    """

    session_id: str
    score: int


class RedisSessionRow:
    """
    Where one session is written, and what is written there.
    """

    @staticmethod
    def session_key(key_prefix: str, session_id: str) -> str:
        """
        The hash holding one session.
        """
        return KEY_SEPARATOR.join((key_prefix, SESSION_KEY_SEGMENT, session_id))

    @staticmethod
    def deadline_index_key(key_prefix: str) -> str:
        """
        The sorted set holding every session's deadline.
        """
        return KEY_SEPARATOR.join((key_prefix, DEADLINE_INDEX_KEY_SEGMENT))

    @staticmethod
    def encode_session(session: SessionObj) -> bytes:
        """
        The bytes written to the data field.
        """
        return ProtobufMessageUtils.message_to_bytes(session)

    @staticmethod
    def decode_session(data: bytes | str) -> SessionObj:
        """
        The session a data field holds.

        A field comes back as text only from a client built to decode its
        responses, which is not how this repository builds one.
        """
        return ProtobufMessageUtils.message_from_bytes(RedisSessionRow._as_bytes(data), SessionObj)

    @staticmethod
    def encode_deadline_score(session: SessionObj) -> str:
        """
        The score the session's deadline is indexed under, in whole
        milliseconds, or empty when the session has none.
        """
        if not session.HasField("acts_by"):
            return NO_DEADLINE_SCORE
        return str(session.acts_by.ToMilliseconds())

    @staticmethod
    def timestamp_to_score(instant: Timestamp) -> int:
        return instant.ToMilliseconds()

    @staticmethod
    def range_item_to_index_entry(item: object) -> DeadlineIndexEntry:
        """
        One item of a scored range read, as the client answers it.

        Raises TypeError when the item is not a member and a score, which the
        client answers only when asked for scores.
        """
        if not isinstance(item, tuple) or len(item) != RANGE_ITEM_LENGTH:
            raise TypeError(f"expected a member and a score, got {item!r}")
        member, score = item
        if not isinstance(member, bytes | str) or not isinstance(score, float | int):
            raise TypeError(f"expected a member and a score, got {item!r}")
        return DeadlineIndexEntry(session_id=RedisSessionRow._as_text(member), score=int(score))

    @staticmethod
    def index_entry_to_deadline(entry: DeadlineIndexEntry, version: bytes | str) -> DeadlineObj:
        """
        One index entry, with the version read from the session it names.
        """
        acts_by = Timestamp()
        acts_by.FromMilliseconds(entry.score)
        return DeadlineObj(
            metadata=ObjectMetadata(
                id=entry.session_id, version=int(RedisSessionRow._as_text(version))
            ),
            acts_by=acts_by,
        )

    @staticmethod
    def _as_bytes(data: bytes | str) -> bytes:
        return data.encode(SESSION_ENCODING) if isinstance(data, str) else data

    @staticmethod
    def _as_text(data: bytes | str) -> str:
        return data.decode(SESSION_ENCODING) if isinstance(data, bytes) else data
