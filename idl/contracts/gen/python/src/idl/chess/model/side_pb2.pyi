from idl.chess.model import piece_pb2 as _piece_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ChessSide(_message.Message):
    __slots__ = ("color",)
    COLOR_FIELD_NUMBER: _ClassVar[int]
    color: _piece_pb2.Color
    def __init__(self, color: _Optional[_Union[_piece_pb2.Color, str]] = ...) -> None: ...
