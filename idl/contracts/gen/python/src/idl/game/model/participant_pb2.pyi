from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Participant(_message.Message):
    __slots__ = ("number", "player_id", "role")
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    number: int
    player_id: str
    role: _any_pb2.Any
    def __init__(self, number: _Optional[int] = ..., player_id: _Optional[str] = ..., role: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class ParticipantRole(_message.Message):
    __slots__ = ("participant", "role")
    PARTICIPANT_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    participant: int
    role: _any_pb2.Any
    def __init__(self, participant: _Optional[int] = ..., role: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
