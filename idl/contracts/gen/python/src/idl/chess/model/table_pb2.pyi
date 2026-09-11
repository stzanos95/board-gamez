from idl.chess.model import piece_pb2 as _piece_pb2
from idl.lobby.model import seat_pb2 as _seat_pb2
from idl.lobby.model import seat_result_pb2 as _seat_result_pb2
from idl.lobby.model import table_pb2 as _table_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ChessSeat(_message.Message):
    __slots__ = ("number", "status", "player_id", "color")
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    number: int
    status: _seat_pb2.SeatStatus
    player_id: str
    color: _piece_pb2.Color
    def __init__(self, number: _Optional[int] = ..., status: _Optional[_Union[_seat_pb2.SeatStatus, str]] = ..., player_id: _Optional[str] = ..., color: _Optional[_Union[_piece_pb2.Color, str]] = ...) -> None: ...

class ChessTable(_message.Message):
    __slots__ = ("id", "status", "seats", "player_ids", "version")
    ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SEATS_FIELD_NUMBER: _ClassVar[int]
    PLAYER_IDS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    id: str
    status: _table_pb2.TableStatus
    seats: _containers.RepeatedCompositeFieldContainer[ChessSeat]
    player_ids: _containers.RepeatedScalarFieldContainer[str]
    version: int
    def __init__(self, id: _Optional[str] = ..., status: _Optional[_Union[_table_pb2.TableStatus, str]] = ..., seats: _Optional[_Iterable[_Union[ChessSeat, _Mapping]]] = ..., player_ids: _Optional[_Iterable[str]] = ..., version: _Optional[int] = ...) -> None: ...

class ChessSeatChoice(_message.Message):
    __slots__ = ("number", "color")
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    number: int
    color: _piece_pb2.Color
    def __init__(self, number: _Optional[int] = ..., color: _Optional[_Union[_piece_pb2.Color, str]] = ...) -> None: ...

class ChessSeatChoiceCollection(_message.Message):
    __slots__ = ("chess_seat_choice_items",)
    CHESS_SEAT_CHOICE_ITEMS_FIELD_NUMBER: _ClassVar[int]
    chess_seat_choice_items: _containers.RepeatedCompositeFieldContainer[ChessSeatChoice]
    def __init__(self, chess_seat_choice_items: _Optional[_Iterable[_Union[ChessSeatChoice, _Mapping]]] = ...) -> None: ...

class ChessSeatResult(_message.Message):
    __slots__ = ("outcome", "table")
    OUTCOME_FIELD_NUMBER: _ClassVar[int]
    TABLE_FIELD_NUMBER: _ClassVar[int]
    outcome: _seat_result_pb2.SeatOutcome
    table: ChessTable
    def __init__(self, outcome: _Optional[_Union[_seat_result_pb2.SeatOutcome, str]] = ..., table: _Optional[_Union[ChessTable, _Mapping]] = ...) -> None: ...
