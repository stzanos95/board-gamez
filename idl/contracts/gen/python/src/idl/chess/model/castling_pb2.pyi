from idl.chess.model import piece_pb2 as _piece_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CastlingSide(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CASTLING_SIDE_UNSPECIFIED: _ClassVar[CastlingSide]
    CASTLING_SIDE_KINGSIDE: _ClassVar[CastlingSide]
    CASTLING_SIDE_QUEENSIDE: _ClassVar[CastlingSide]
CASTLING_SIDE_UNSPECIFIED: CastlingSide
CASTLING_SIDE_KINGSIDE: CastlingSide
CASTLING_SIDE_QUEENSIDE: CastlingSide

class CastlingRight(_message.Message):
    __slots__ = ("color", "side")
    COLOR_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    color: _piece_pb2.Color
    side: CastlingSide
    def __init__(self, color: _Optional[_Union[_piece_pb2.Color, str]] = ..., side: _Optional[_Union[CastlingSide, str]] = ...) -> None: ...

class CastlingRights(_message.Message):
    __slots__ = ("available",)
    AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    available: _containers.RepeatedCompositeFieldContainer[CastlingRight]
    def __init__(self, available: _Optional[_Iterable[_Union[CastlingRight, _Mapping]]] = ...) -> None: ...
