from idl.lobby.model import table_pb2 as _table_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ReadTableRequest(_message.Message):
    __slots__ = ("table_id",)
    TABLE_ID_FIELD_NUMBER: _ClassVar[int]
    table_id: str
    def __init__(self, table_id: _Optional[str] = ...) -> None: ...

class ReadTableResponse(_message.Message):
    __slots__ = ("table",)
    TABLE_FIELD_NUMBER: _ClassVar[int]
    table: _table_pb2.Table
    def __init__(self, table: _Optional[_Union[_table_pb2.Table, _Mapping]] = ...) -> None: ...

class DeleteTableRequest(_message.Message):
    __slots__ = ("table_id", "expected_version")
    TABLE_ID_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_VERSION_FIELD_NUMBER: _ClassVar[int]
    table_id: str
    expected_version: int
    def __init__(self, table_id: _Optional[str] = ..., expected_version: _Optional[int] = ...) -> None: ...

class DeleteTableResponse(_message.Message):
    __slots__ = ("table_id",)
    TABLE_ID_FIELD_NUMBER: _ClassVar[int]
    table_id: str
    def __init__(self, table_id: _Optional[str] = ...) -> None: ...

class ListTableRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListTableResponse(_message.Message):
    __slots__ = ("collection",)
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    collection: _table_pb2.TableCollection
    def __init__(self, collection: _Optional[_Union[_table_pb2.TableCollection, _Mapping]] = ...) -> None: ...
