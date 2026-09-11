"""
The keys and fields one session occupies in Redis.

A session is a hash of two fields: the version as decimal text, and the session
in protobuf's binary wire format. The version is readable without decoding the
session, which is what lets a compare-and-set run inside Redis.
"""

from core.protobuf.message_utils import ProtobufMessageUtils
from idl.game.obj.session_pb2 import SessionObj

VERSION_FIELD = "version"
DATA_FIELD = "data"

KEY_SEPARATOR = ":"
SESSION_KEY_SEGMENT = "session"
SESSION_ENCODING = "utf-8"


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
        return ProtobufMessageUtils.message_from_bytes(
            data.encode(SESSION_ENCODING) if isinstance(data, str) else data, SessionObj
        )
