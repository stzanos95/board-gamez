from idl.chess.model import table_pb2 as _table_pb2
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
    table: _table_pb2.ChessTable
    def __init__(self, table: _Optional[_Union[_table_pb2.ChessTable, _Mapping]] = ...) -> None: ...

class ListSeatChoiceRequest(_message.Message):
    __slots__ = ("table_id", "player_id")
    TABLE_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    table_id: str
    player_id: str
    def __init__(self, table_id: _Optional[str] = ..., player_id: _Optional[str] = ...) -> None: ...

class ListSeatChoiceResponse(_message.Message):
    __slots__ = ("collection",)
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    collection: _table_pb2.ChessSeatChoiceCollection
    def __init__(self, collection: _Optional[_Union[_table_pb2.ChessSeatChoiceCollection, _Mapping]] = ...) -> None: ...

class TakeSeatRequest(_message.Message):
    __slots__ = ("table_id", "player_id", "choice", "expected_version")
    TABLE_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    CHOICE_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_VERSION_FIELD_NUMBER: _ClassVar[int]
    table_id: str
    player_id: str
    choice: _table_pb2.ChessSeatChoice
    expected_version: int
    def __init__(self, table_id: _Optional[str] = ..., player_id: _Optional[str] = ..., choice: _Optional[_Union[_table_pb2.ChessSeatChoice, _Mapping]] = ..., expected_version: _Optional[int] = ...) -> None: ...

class TakeSeatResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _table_pb2.ChessSeatResult
    def __init__(self, result: _Optional[_Union[_table_pb2.ChessSeatResult, _Mapping]] = ...) -> None: ...
