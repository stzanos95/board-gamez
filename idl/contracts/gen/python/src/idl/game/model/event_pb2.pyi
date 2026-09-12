from google.protobuf import any_pb2 as _any_pb2
from idl.game.model import game_type_pb2 as _game_type_pb2
from idl.game.model import participant_pb2 as _participant_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SessionStarted(_message.Message):
    __slots__ = ("session_id", "game_type", "participants", "version")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    GAME_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANTS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    game_type: _game_type_pb2.GameType
    participants: _containers.RepeatedCompositeFieldContainer[_participant_pb2.Participant]
    version: int
    def __init__(self, session_id: _Optional[str] = ..., game_type: _Optional[_Union[_game_type_pb2.GameType, str]] = ..., participants: _Optional[_Iterable[_Union[_participant_pb2.Participant, _Mapping]]] = ..., version: _Optional[int] = ...) -> None: ...

class CommandApplied(_message.Message):
    __slots__ = ("session_id", "participant", "command_id", "action", "is_over", "version")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_FIELD_NUMBER: _ClassVar[int]
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    IS_OVER_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    participant: int
    command_id: str
    action: _any_pb2.Any
    is_over: bool
    version: int
    def __init__(self, session_id: _Optional[str] = ..., participant: _Optional[int] = ..., command_id: _Optional[str] = ..., action: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., is_over: bool = ..., version: _Optional[int] = ...) -> None: ...

class ParticipantWithdrawn(_message.Message):
    __slots__ = ("session_id", "participant", "is_over", "version")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_FIELD_NUMBER: _ClassVar[int]
    IS_OVER_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    participant: int
    is_over: bool
    version: int
    def __init__(self, session_id: _Optional[str] = ..., participant: _Optional[int] = ..., is_over: bool = ..., version: _Optional[int] = ...) -> None: ...

class SessionChanged(_message.Message):
    __slots__ = ("session_id", "version")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    version: int
    def __init__(self, session_id: _Optional[str] = ..., version: _Optional[int] = ...) -> None: ...
