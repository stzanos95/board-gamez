from idl.game.model import session_pb2 as _session_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class WithdrawalOutcome(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WITHDRAWAL_OUTCOME_UNSPECIFIED: _ClassVar[WithdrawalOutcome]
    WITHDRAWAL_OUTCOME_WITHDRAWN: _ClassVar[WithdrawalOutcome]
    WITHDRAWAL_OUTCOME_SESSION_NOT_FOUND: _ClassVar[WithdrawalOutcome]
    WITHDRAWAL_OUTCOME_NOT_A_PARTICIPANT: _ClassVar[WithdrawalOutcome]
    WITHDRAWAL_OUTCOME_NOT_IN_GAME: _ClassVar[WithdrawalOutcome]
    WITHDRAWAL_OUTCOME_GAME_OVER: _ClassVar[WithdrawalOutcome]
    WITHDRAWAL_OUTCOME_VERSION_MOVED: _ClassVar[WithdrawalOutcome]
WITHDRAWAL_OUTCOME_UNSPECIFIED: WithdrawalOutcome
WITHDRAWAL_OUTCOME_WITHDRAWN: WithdrawalOutcome
WITHDRAWAL_OUTCOME_SESSION_NOT_FOUND: WithdrawalOutcome
WITHDRAWAL_OUTCOME_NOT_A_PARTICIPANT: WithdrawalOutcome
WITHDRAWAL_OUTCOME_NOT_IN_GAME: WithdrawalOutcome
WITHDRAWAL_OUTCOME_GAME_OVER: WithdrawalOutcome
WITHDRAWAL_OUTCOME_VERSION_MOVED: WithdrawalOutcome

class WithdrawalResult(_message.Message):
    __slots__ = ("outcome", "session")
    OUTCOME_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    outcome: WithdrawalOutcome
    session: _session_pb2.SessionView
    def __init__(self, outcome: _Optional[_Union[WithdrawalOutcome, str]] = ..., session: _Optional[_Union[_session_pb2.SessionView, _Mapping]] = ...) -> None: ...
