from google.protobuf import any_pb2 as _any_pb2
from idl.game.model import command_result_pb2 as _command_result_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ApplyCommandRequest(_message.Message):
    __slots__ = ("session_id", "command_id", "player_id", "action", "expected_version")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_VERSION_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    command_id: str
    player_id: str
    action: _any_pb2.Any
    expected_version: int
    def __init__(self, session_id: _Optional[str] = ..., command_id: _Optional[str] = ..., player_id: _Optional[str] = ..., action: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., expected_version: _Optional[int] = ...) -> None: ...

class ApplyCommandResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _command_result_pb2.CommandResult
    def __init__(self, result: _Optional[_Union[_command_result_pb2.CommandResult, _Mapping]] = ...) -> None: ...
