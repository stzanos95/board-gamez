from google.protobuf import any_pb2 as _any_pb2
from idl.game.model import game_type_pb2 as _game_type_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TableCreated(_message.Message):
    __slots__ = ("table_id", "game_type", "player_id", "version")
    TABLE_ID_FIELD_NUMBER: _ClassVar[int]
    GAME_TYPE_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    table_id: str
    game_type: _game_type_pb2.GameType
    player_id: str
    version: int
    def __init__(self, table_id: _Optional[str] = ..., game_type: _Optional[_Union[_game_type_pb2.GameType, str]] = ..., player_id: _Optional[str] = ..., version: _Optional[int] = ...) -> None: ...

class PlayerJoined(_message.Message):
    __slots__ = ("table_id", "player_id", "version")
    TABLE_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    table_id: str
    player_id: str
    version: int
    def __init__(self, table_id: _Optional[str] = ..., player_id: _Optional[str] = ..., version: _Optional[int] = ...) -> None: ...

class SeatTaken(_message.Message):
    __slots__ = ("table_id", "player_id", "seat_number", "role", "version")
    TABLE_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    SEAT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    table_id: str
    player_id: str
    seat_number: int
    role: _any_pb2.Any
    version: int
    def __init__(self, table_id: _Optional[str] = ..., player_id: _Optional[str] = ..., seat_number: _Optional[int] = ..., role: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., version: _Optional[int] = ...) -> None: ...

class SeatVacated(_message.Message):
    __slots__ = ("table_id", "player_id", "seat_number", "version")
    TABLE_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    SEAT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    table_id: str
    player_id: str
    seat_number: int
    version: int
    def __init__(self, table_id: _Optional[str] = ..., player_id: _Optional[str] = ..., seat_number: _Optional[int] = ..., version: _Optional[int] = ...) -> None: ...

class PlayerLeft(_message.Message):
    __slots__ = ("table_id", "player_id", "seat_number", "version")
    TABLE_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    SEAT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    table_id: str
    player_id: str
    seat_number: int
    version: int
    def __init__(self, table_id: _Optional[str] = ..., player_id: _Optional[str] = ..., seat_number: _Optional[int] = ..., version: _Optional[int] = ...) -> None: ...

class TableClosed(_message.Message):
    __slots__ = ("table_id",)
    TABLE_ID_FIELD_NUMBER: _ClassVar[int]
    table_id: str
    def __init__(self, table_id: _Optional[str] = ...) -> None: ...

class TableChanged(_message.Message):
    __slots__ = ("table_id", "version")
    TABLE_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    table_id: str
    version: int
    def __init__(self, table_id: _Optional[str] = ..., version: _Optional[int] = ...) -> None: ...
