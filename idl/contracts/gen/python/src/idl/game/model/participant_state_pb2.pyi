from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ParticipantStateKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PARTICIPANT_STATE_KIND_UNSPECIFIED: _ClassVar[ParticipantStateKind]
    PARTICIPANT_STATE_KIND_HOLDING: _ClassVar[ParticipantStateKind]
    PARTICIPANT_STATE_KIND_LAST_ONE: _ClassVar[ParticipantStateKind]
    PARTICIPANT_STATE_KIND_WITHDRAWN: _ClassVar[ParticipantStateKind]
PARTICIPANT_STATE_KIND_UNSPECIFIED: ParticipantStateKind
PARTICIPANT_STATE_KIND_HOLDING: ParticipantStateKind
PARTICIPANT_STATE_KIND_LAST_ONE: ParticipantStateKind
PARTICIPANT_STATE_KIND_WITHDRAWN: ParticipantStateKind

class ParticipantState(_message.Message):
    __slots__ = ("kind", "count")
    KIND_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    kind: ParticipantStateKind
    count: int
    def __init__(self, kind: _Optional[_Union[ParticipantStateKind, str]] = ..., count: _Optional[int] = ...) -> None: ...

class ParticipantStatus(_message.Message):
    __slots__ = ("participant", "states")
    PARTICIPANT_FIELD_NUMBER: _ClassVar[int]
    STATES_FIELD_NUMBER: _ClassVar[int]
    participant: int
    states: _containers.RepeatedCompositeFieldContainer[ParticipantState]
    def __init__(self, participant: _Optional[int] = ..., states: _Optional[_Iterable[_Union[ParticipantState, _Mapping]]] = ...) -> None: ...
