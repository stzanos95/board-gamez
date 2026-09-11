from google.protobuf import any_pb2 as _any_pb2
from idl.game.model import command_outcome_pb2 as _command_outcome_pb2
from idl.game.model import session_pb2 as _session_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ApplyCommandRequest(_message.Message):
    __slots__ = ("session_id", "command_id", "action", "expected_version")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_VERSION_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    command_id: str
    action: _any_pb2.Any
    expected_version: int
    def __init__(self, session_id: _Optional[str] = ..., command_id: _Optional[str] = ..., action: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., expected_version: _Optional[int] = ...) -> None: ...

class ApplyCommandResponse(_message.Message):
    __slots__ = ("outcome", "session")
    OUTCOME_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    outcome: _command_outcome_pb2.CommandOutcome
    session: _session_pb2.SessionView
    def __init__(self, outcome: _Optional[_Union[_command_outcome_pb2.CommandOutcome, str]] = ..., session: _Optional[_Union[_session_pb2.SessionView, _Mapping]] = ...) -> None: ...
