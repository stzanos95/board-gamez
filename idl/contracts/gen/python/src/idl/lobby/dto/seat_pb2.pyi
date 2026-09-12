from idl.game.model import game_type_pb2 as _game_type_pb2
from idl.lobby.model import seat_result_pb2 as _seat_result_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateTableRequest(_message.Message):
    __slots__ = ("game_type", "seat_count", "player_id")
    GAME_TYPE_FIELD_NUMBER: _ClassVar[int]
    SEAT_COUNT_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    game_type: _game_type_pb2.GameType
    seat_count: int
    player_id: str
    def __init__(self, game_type: _Optional[_Union[_game_type_pb2.GameType, str]] = ..., seat_count: _Optional[int] = ..., player_id: _Optional[str] = ...) -> None: ...

class CreateTableResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _seat_result_pb2.SeatResult
    def __init__(self, result: _Optional[_Union[_seat_result_pb2.SeatResult, _Mapping]] = ...) -> None: ...

class JoinTableRequest(_message.Message):
    __slots__ = ("table_id", "player_id")
    TABLE_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    table_id: str
    player_id: str
    def __init__(self, table_id: _Optional[str] = ..., player_id: _Optional[str] = ...) -> None: ...

class JoinTableResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _seat_result_pb2.SeatResult
    def __init__(self, result: _Optional[_Union[_seat_result_pb2.SeatResult, _Mapping]] = ...) -> None: ...

class VacateSeatRequest(_message.Message):
    __slots__ = ("table_id", "player_id")
    TABLE_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    table_id: str
    player_id: str
    def __init__(self, table_id: _Optional[str] = ..., player_id: _Optional[str] = ...) -> None: ...

class VacateSeatResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _seat_result_pb2.SeatResult
    def __init__(self, result: _Optional[_Union[_seat_result_pb2.SeatResult, _Mapping]] = ...) -> None: ...

class LeaveTableRequest(_message.Message):
    __slots__ = ("table_id", "player_id")
    TABLE_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    table_id: str
    player_id: str
    def __init__(self, table_id: _Optional[str] = ..., player_id: _Optional[str] = ...) -> None: ...

class LeaveTableResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _seat_result_pb2.SeatResult
    def __init__(self, result: _Optional[_Union[_seat_result_pb2.SeatResult, _Mapping]] = ...) -> None: ...
