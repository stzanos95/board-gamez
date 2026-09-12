from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from idl.game.model import game_result_pb2 as _game_result_pb2
from idl.game.model import participant_state_pb2 as _participant_state_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GameState(_message.Message):
    __slots__ = ("payload", "participants_to_act", "result", "acts_within", "participant_statuses")
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANTS_TO_ACT_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    ACTS_WITHIN_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_STATUSES_FIELD_NUMBER: _ClassVar[int]
    payload: _any_pb2.Any
    participants_to_act: _containers.RepeatedScalarFieldContainer[int]
    result: _game_result_pb2.GameResult
    acts_within: _duration_pb2.Duration
    participant_statuses: _containers.RepeatedCompositeFieldContainer[_participant_state_pb2.ParticipantStatus]
    def __init__(self, payload: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., participants_to_act: _Optional[_Iterable[int]] = ..., result: _Optional[_Union[_game_result_pb2.GameResult, _Mapping]] = ..., acts_within: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., participant_statuses: _Optional[_Iterable[_Union[_participant_state_pb2.ParticipantStatus, _Mapping]]] = ...) -> None: ...
