from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

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
