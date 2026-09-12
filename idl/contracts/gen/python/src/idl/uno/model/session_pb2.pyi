from idl.game.model import command_result_pb2 as _command_result_pb2
from idl.uno.model import view_pb2 as _view_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UnoSession(_message.Message):
    __slots__ = ("id", "view", "participant", "last_command_id", "version")
    ID_FIELD_NUMBER: _ClassVar[int]
    VIEW_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_FIELD_NUMBER: _ClassVar[int]
    LAST_COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    id: str
    view: _view_pb2.UnoView
    participant: int
    last_command_id: str
    version: int
    def __init__(self, id: _Optional[str] = ..., view: _Optional[_Union[_view_pb2.UnoView, _Mapping]] = ..., participant: _Optional[int] = ..., last_command_id: _Optional[str] = ..., version: _Optional[int] = ...) -> None: ...

class ActionResult(_message.Message):
    __slots__ = ("outcome", "session")
    OUTCOME_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    outcome: _command_result_pb2.CommandOutcome
    session: UnoSession
    def __init__(self, outcome: _Optional[_Union[_command_result_pb2.CommandOutcome, str]] = ..., session: _Optional[_Union[UnoSession, _Mapping]] = ...) -> None: ...
