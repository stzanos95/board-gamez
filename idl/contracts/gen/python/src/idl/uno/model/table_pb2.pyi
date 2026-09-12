from idl.lobby.model import seat_pb2 as _seat_pb2
from idl.lobby.model import seat_result_pb2 as _seat_result_pb2
from idl.lobby.model import table_pb2 as _table_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UnoSeat(_message.Message):
    __slots__ = ("number", "status", "player_id")
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    number: int
    status: _seat_pb2.SeatStatus
    player_id: str
    def __init__(self, number: _Optional[int] = ..., status: _Optional[_Union[_seat_pb2.SeatStatus, str]] = ..., player_id: _Optional[str] = ...) -> None: ...

class UnoTable(_message.Message):
    __slots__ = ("id", "status", "seats", "player_ids", "version")
    ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SEATS_FIELD_NUMBER: _ClassVar[int]
    PLAYER_IDS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    id: str
    status: _table_pb2.TableStatus
    seats: _containers.RepeatedCompositeFieldContainer[UnoSeat]
    player_ids: _containers.RepeatedScalarFieldContainer[str]
    version: int
    def __init__(self, id: _Optional[str] = ..., status: _Optional[_Union[_table_pb2.TableStatus, str]] = ..., seats: _Optional[_Iterable[_Union[UnoSeat, _Mapping]]] = ..., player_ids: _Optional[_Iterable[str]] = ..., version: _Optional[int] = ...) -> None: ...

class UnoSeatChoice(_message.Message):
    __slots__ = ("number",)
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    number: int
    def __init__(self, number: _Optional[int] = ...) -> None: ...

class UnoSeatChoiceCollection(_message.Message):
    __slots__ = ("uno_seat_choice_items",)
    UNO_SEAT_CHOICE_ITEMS_FIELD_NUMBER: _ClassVar[int]
    uno_seat_choice_items: _containers.RepeatedCompositeFieldContainer[UnoSeatChoice]
    def __init__(self, uno_seat_choice_items: _Optional[_Iterable[_Union[UnoSeatChoice, _Mapping]]] = ...) -> None: ...

class UnoSeatResult(_message.Message):
    __slots__ = ("outcome", "table")
    OUTCOME_FIELD_NUMBER: _ClassVar[int]
    TABLE_FIELD_NUMBER: _ClassVar[int]
    outcome: _seat_result_pb2.SeatOutcome
    table: UnoTable
    def __init__(self, outcome: _Optional[_Union[_seat_result_pb2.SeatOutcome, str]] = ..., table: _Optional[_Union[UnoTable, _Mapping]] = ...) -> None: ...
