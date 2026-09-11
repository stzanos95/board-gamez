from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ParticipantOutcome(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PARTICIPANT_OUTCOME_UNSPECIFIED: _ClassVar[ParticipantOutcome]
    PARTICIPANT_OUTCOME_WON: _ClassVar[ParticipantOutcome]
    PARTICIPANT_OUTCOME_LOST: _ClassVar[ParticipantOutcome]
    PARTICIPANT_OUTCOME_DRAW: _ClassVar[ParticipantOutcome]
PARTICIPANT_OUTCOME_UNSPECIFIED: ParticipantOutcome
PARTICIPANT_OUTCOME_WON: ParticipantOutcome
PARTICIPANT_OUTCOME_LOST: ParticipantOutcome
PARTICIPANT_OUTCOME_DRAW: ParticipantOutcome

class ParticipantResult(_message.Message):
    __slots__ = ("participant", "outcome")
    PARTICIPANT_FIELD_NUMBER: _ClassVar[int]
    OUTCOME_FIELD_NUMBER: _ClassVar[int]
    participant: int
    outcome: ParticipantOutcome
    def __init__(self, participant: _Optional[int] = ..., outcome: _Optional[_Union[ParticipantOutcome, str]] = ...) -> None: ...

class GameResult(_message.Message):
    __slots__ = ("participant_items",)
    PARTICIPANT_ITEMS_FIELD_NUMBER: _ClassVar[int]
    participant_items: _containers.RepeatedCompositeFieldContainer[ParticipantResult]
    def __init__(self, participant_items: _Optional[_Iterable[_Union[ParticipantResult, _Mapping]]] = ...) -> None: ...
