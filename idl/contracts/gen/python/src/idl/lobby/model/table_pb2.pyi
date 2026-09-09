from idl.lobby.model import game_type_pb2 as _game_type_pb2
from idl.lobby.model import seat_pb2 as _seat_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TableStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TABLE_STATUS_UNSPECIFIED: _ClassVar[TableStatus]
    TABLE_STATUS_WAITING: _ClassVar[TableStatus]
    TABLE_STATUS_IN_PROGRESS: _ClassVar[TableStatus]
    TABLE_STATUS_FINISHED: _ClassVar[TableStatus]
    TABLE_STATUS_ABANDONED: _ClassVar[TableStatus]
TABLE_STATUS_UNSPECIFIED: TableStatus
TABLE_STATUS_WAITING: TableStatus
TABLE_STATUS_IN_PROGRESS: TableStatus
TABLE_STATUS_FINISHED: TableStatus
TABLE_STATUS_ABANDONED: TableStatus

class Table(_message.Message):
    __slots__ = ("id", "game_type", "status", "seats", "version")
    ID_FIELD_NUMBER: _ClassVar[int]
    GAME_TYPE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SEATS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    id: str
    game_type: _game_type_pb2.GameType
    status: TableStatus
    seats: _containers.RepeatedCompositeFieldContainer[_seat_pb2.Seat]
    version: int
    def __init__(self, id: _Optional[str] = ..., game_type: _Optional[_Union[_game_type_pb2.GameType, str]] = ..., status: _Optional[_Union[TableStatus, str]] = ..., seats: _Optional[_Iterable[_Union[_seat_pb2.Seat, _Mapping]]] = ..., version: _Optional[int] = ...) -> None: ...

class TableCollection(_message.Message):
    __slots__ = ("table_items",)
    TABLE_ITEMS_FIELD_NUMBER: _ClassVar[int]
    table_items: _containers.RepeatedCompositeFieldContainer[Table]
    def __init__(self, table_items: _Optional[_Iterable[_Union[Table, _Mapping]]] = ...) -> None: ...
