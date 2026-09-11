from google.protobuf import any_pb2 as _any_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SeatStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SEAT_STATUS_UNSPECIFIED: _ClassVar[SeatStatus]
    SEAT_STATUS_OPEN: _ClassVar[SeatStatus]
    SEAT_STATUS_OCCUPIED: _ClassVar[SeatStatus]
SEAT_STATUS_UNSPECIFIED: SeatStatus
SEAT_STATUS_OPEN: SeatStatus
SEAT_STATUS_OCCUPIED: SeatStatus

class Seat(_message.Message):
    __slots__ = ("number", "status", "player_id", "role")
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    number: int
    status: SeatStatus
    player_id: str
    role: _any_pb2.Any
    def __init__(self, number: _Optional[int] = ..., status: _Optional[_Union[SeatStatus, str]] = ..., player_id: _Optional[str] = ..., role: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class SeatChoice(_message.Message):
    __slots__ = ("number", "role")
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    number: int
    role: _any_pb2.Any
    def __init__(self, number: _Optional[int] = ..., role: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class SeatChoiceCollection(_message.Message):
    __slots__ = ("seat_choice_items",)
    SEAT_CHOICE_ITEMS_FIELD_NUMBER: _ClassVar[int]
    seat_choice_items: _containers.RepeatedCompositeFieldContainer[SeatChoice]
    def __init__(self, seat_choice_items: _Optional[_Iterable[_Union[SeatChoice, _Mapping]]] = ...) -> None: ...
