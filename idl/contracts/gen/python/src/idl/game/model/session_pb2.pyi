from google.protobuf import timestamp_pb2 as _timestamp_pb2
from idl.game.model import game_state_pb2 as _game_state_pb2
from idl.game.model import game_type_pb2 as _game_type_pb2
from idl.game.model import participant_pb2 as _participant_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Session(_message.Message):
    __slots__ = ("id", "game_type", "participants", "state", "last_command_id", "version", "acts_by")
    ID_FIELD_NUMBER: _ClassVar[int]
    GAME_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANTS_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    LAST_COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ACTS_BY_FIELD_NUMBER: _ClassVar[int]
    id: str
    game_type: _game_type_pb2.GameType
    participants: _containers.RepeatedCompositeFieldContainer[_participant_pb2.Participant]
    state: _game_state_pb2.GameState
    last_command_id: str
    version: int
    acts_by: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., game_type: _Optional[_Union[_game_type_pb2.GameType, str]] = ..., participants: _Optional[_Iterable[_Union[_participant_pb2.Participant, _Mapping]]] = ..., state: _Optional[_Union[_game_state_pb2.GameState, _Mapping]] = ..., last_command_id: _Optional[str] = ..., version: _Optional[int] = ..., acts_by: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class SessionView(_message.Message):
    __slots__ = ("id", "game_type", "participants", "participant", "state", "last_command_id", "version", "acts_by")
    ID_FIELD_NUMBER: _ClassVar[int]
    GAME_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANTS_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    LAST_COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ACTS_BY_FIELD_NUMBER: _ClassVar[int]
    id: str
    game_type: _game_type_pb2.GameType
    participants: _containers.RepeatedCompositeFieldContainer[_participant_pb2.Participant]
    participant: int
    state: _game_state_pb2.GameState
    last_command_id: str
    version: int
    acts_by: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., game_type: _Optional[_Union[_game_type_pb2.GameType, str]] = ..., participants: _Optional[_Iterable[_Union[_participant_pb2.Participant, _Mapping]]] = ..., participant: _Optional[int] = ..., state: _Optional[_Union[_game_state_pb2.GameState, _Mapping]] = ..., last_command_id: _Optional[str] = ..., version: _Optional[int] = ..., acts_by: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
