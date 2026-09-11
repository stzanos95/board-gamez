from idl.chess.model import move_pb2 as _move_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Resignation(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ChessAction(_message.Message):
    __slots__ = ("move", "resignation")
    MOVE_FIELD_NUMBER: _ClassVar[int]
    RESIGNATION_FIELD_NUMBER: _ClassVar[int]
    move: _move_pb2.CoordinateMove
    resignation: Resignation
    def __init__(self, move: _Optional[_Union[_move_pb2.CoordinateMove, _Mapping]] = ..., resignation: _Optional[_Union[Resignation, _Mapping]] = ...) -> None: ...
