from idl.lobby.model import table_pb2 as _table_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SeatOutcome(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SEAT_OUTCOME_UNSPECIFIED: _ClassVar[SeatOutcome]
    SEAT_OUTCOME_TAKEN: _ClassVar[SeatOutcome]
    SEAT_OUTCOME_TABLE_NOT_FOUND: _ClassVar[SeatOutcome]
    SEAT_OUTCOME_NOT_OFFERED: _ClassVar[SeatOutcome]
    SEAT_OUTCOME_VERSION_MOVED: _ClassVar[SeatOutcome]
    SEAT_OUTCOME_VACATED: _ClassVar[SeatOutcome]
    SEAT_OUTCOME_LEFT: _ClassVar[SeatOutcome]
    SEAT_OUTCOME_NOT_SEATED: _ClassVar[SeatOutcome]
    SEAT_OUTCOME_NOT_AT_TABLE: _ClassVar[SeatOutcome]
SEAT_OUTCOME_UNSPECIFIED: SeatOutcome
SEAT_OUTCOME_TAKEN: SeatOutcome
SEAT_OUTCOME_TABLE_NOT_FOUND: SeatOutcome
SEAT_OUTCOME_NOT_OFFERED: SeatOutcome
SEAT_OUTCOME_VERSION_MOVED: SeatOutcome
SEAT_OUTCOME_VACATED: SeatOutcome
SEAT_OUTCOME_LEFT: SeatOutcome
SEAT_OUTCOME_NOT_SEATED: SeatOutcome
SEAT_OUTCOME_NOT_AT_TABLE: SeatOutcome

class SeatResult(_message.Message):
    __slots__ = ("outcome", "table")
    OUTCOME_FIELD_NUMBER: _ClassVar[int]
    TABLE_FIELD_NUMBER: _ClassVar[int]
    outcome: SeatOutcome
    table: _table_pb2.Table
    def __init__(self, outcome: _Optional[_Union[SeatOutcome, str]] = ..., table: _Optional[_Union[_table_pb2.Table, _Mapping]] = ...) -> None: ...
