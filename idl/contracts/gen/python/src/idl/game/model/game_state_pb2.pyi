from google.protobuf import any_pb2 as _any_pb2
from idl.game.model import game_result_pb2 as _game_result_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GameState(_message.Message):
    __slots__ = ("payload", "participant_to_act", "result")
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_TO_ACT_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    payload: _any_pb2.Any
    participant_to_act: int
    result: _game_result_pb2.GameResult
    def __init__(self, payload: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., participant_to_act: _Optional[int] = ..., result: _Optional[_Union[_game_result_pb2.GameResult, _Mapping]] = ...) -> None: ...
