from idl.game.model import session_pb2 as _session_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CommandOutcome(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    COMMAND_OUTCOME_UNSPECIFIED: _ClassVar[CommandOutcome]
    COMMAND_OUTCOME_APPLIED: _ClassVar[CommandOutcome]
    COMMAND_OUTCOME_ALREADY_APPLIED: _ClassVar[CommandOutcome]
    COMMAND_OUTCOME_SESSION_NOT_FOUND: _ClassVar[CommandOutcome]
    COMMAND_OUTCOME_NOT_A_PARTICIPANT: _ClassVar[CommandOutcome]
    COMMAND_OUTCOME_GAME_OVER: _ClassVar[CommandOutcome]
    COMMAND_OUTCOME_VERSION_MOVED: _ClassVar[CommandOutcome]
    COMMAND_OUTCOME_OUT_OF_TURN: _ClassVar[CommandOutcome]
    COMMAND_OUTCOME_ILLEGAL_ACTION: _ClassVar[CommandOutcome]
COMMAND_OUTCOME_UNSPECIFIED: CommandOutcome
COMMAND_OUTCOME_APPLIED: CommandOutcome
COMMAND_OUTCOME_ALREADY_APPLIED: CommandOutcome
COMMAND_OUTCOME_SESSION_NOT_FOUND: CommandOutcome
COMMAND_OUTCOME_NOT_A_PARTICIPANT: CommandOutcome
COMMAND_OUTCOME_GAME_OVER: CommandOutcome
COMMAND_OUTCOME_VERSION_MOVED: CommandOutcome
COMMAND_OUTCOME_OUT_OF_TURN: CommandOutcome
COMMAND_OUTCOME_ILLEGAL_ACTION: CommandOutcome

class CommandResult(_message.Message):
    __slots__ = ("outcome", "session")
    OUTCOME_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    outcome: CommandOutcome
    session: _session_pb2.SessionView
    def __init__(self, outcome: _Optional[_Union[CommandOutcome, str]] = ..., session: _Optional[_Union[_session_pb2.SessionView, _Mapping]] = ...) -> None: ...
