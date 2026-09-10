"""
The keys and fields one table occupies in Redis.

A table is a hash of two fields: the version as decimal text, and the table in
protobuf's binary wire format. The version is readable without decoding the
table, which is what lets a compare-and-set run inside Redis.
"""

from core.protobuf.message_utils import ProtobufMessageUtils
from idl.lobby.obj.table_pb2 import TableObj

VERSION_FIELD = "version"
DATA_FIELD = "data"

KEY_SEPARATOR = ":"
TABLE_KEY_SEGMENT = "table"
ANY_TABLE_ID = "*"
TABLE_ENCODING = "utf-8"


class RedisTableRow:
    """
    Where one table is written, and what is written there.
    """

    @staticmethod
    def table_key(key_prefix: str, table_id: str) -> str:
        """
        The hash holding one table.
        """
        return KEY_SEPARATOR.join((key_prefix, TABLE_KEY_SEGMENT, table_id))

    @staticmethod
    def every_table_key(key_prefix: str) -> str:
        """
        The pattern matching the hash of every table under this prefix.
        """
        return RedisTableRow.table_key(key_prefix, ANY_TABLE_ID)

    @staticmethod
    def encode_table(table: TableObj) -> bytes:
        """
        The bytes written to the data field.
        """
        return ProtobufMessageUtils.message_to_bytes(table)

    @staticmethod
    def decode_table(data: bytes | str) -> TableObj:
        """
        The table a data field holds.

        A field comes back as text only from a client built to decode its
        responses, which is not how this repository builds one.
        """
        return ProtobufMessageUtils.message_from_bytes(
            data.encode(TABLE_ENCODING) if isinstance(data, str) else data, TableObj
        )
