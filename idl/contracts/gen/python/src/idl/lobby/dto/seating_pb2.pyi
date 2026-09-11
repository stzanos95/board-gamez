from idl.lobby.model import seat_pb2 as _seat_pb2
from idl.lobby.model import table_pb2 as _table_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListSeatChoiceRequest(_message.Message):
    __slots__ = ("table", "player_id")
    TABLE_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    table: _table_pb2.Table
    player_id: str
    def __init__(self, table: _Optional[_Union[_table_pb2.Table, _Mapping]] = ..., player_id: _Optional[str] = ...) -> None: ...

class ListSeatChoiceResponse(_message.Message):
    __slots__ = ("collection",)
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    collection: _seat_pb2.SeatChoiceCollection
    def __init__(self, collection: _Optional[_Union[_seat_pb2.SeatChoiceCollection, _Mapping]] = ...) -> None: ...
