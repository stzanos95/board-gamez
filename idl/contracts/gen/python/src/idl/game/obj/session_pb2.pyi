from idl.core.obj import object_metadata_pb2 as _object_metadata_pb2
from idl.game.model import game_state_pb2 as _game_state_pb2
from idl.game.model import game_type_pb2 as _game_type_pb2
from idl.game.model import participant_pb2 as _participant_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SessionObj(_message.Message):
    __slots__ = ("metadata", "game_type", "participants", "state", "last_command_id")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    GAME_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANTS_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    LAST_COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    metadata: _object_metadata_pb2.ObjectMetadata
    game_type: _game_type_pb2.GameType
    participants: _containers.RepeatedCompositeFieldContainer[_participant_pb2.Participant]
    state: _game_state_pb2.GameState
    last_command_id: str
    def __init__(self, metadata: _Optional[_Union[_object_metadata_pb2.ObjectMetadata, _Mapping]] = ..., game_type: _Optional[_Union[_game_type_pb2.GameType, str]] = ..., participants: _Optional[_Iterable[_Union[_participant_pb2.Participant, _Mapping]]] = ..., state: _Optional[_Union[_game_state_pb2.GameState, _Mapping]] = ..., last_command_id: _Optional[str] = ...) -> None: ...
