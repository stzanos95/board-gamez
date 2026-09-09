from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

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
    __slots__ = ("number", "status", "player_id")
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    number: int
    status: SeatStatus
    player_id: str
    def __init__(self, number: _Optional[int] = ..., status: _Optional[_Union[SeatStatus, str]] = ..., player_id: _Optional[str] = ...) -> None: ...
