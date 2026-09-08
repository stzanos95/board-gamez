from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Color(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    COLOR_UNSPECIFIED: _ClassVar[Color]
    COLOR_WHITE: _ClassVar[Color]
    COLOR_BLACK: _ClassVar[Color]

class PieceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PIECE_TYPE_UNSPECIFIED: _ClassVar[PieceType]
    PIECE_TYPE_PAWN: _ClassVar[PieceType]
    PIECE_TYPE_KNIGHT: _ClassVar[PieceType]
    PIECE_TYPE_BISHOP: _ClassVar[PieceType]
    PIECE_TYPE_ROOK: _ClassVar[PieceType]
    PIECE_TYPE_QUEEN: _ClassVar[PieceType]
    PIECE_TYPE_KING: _ClassVar[PieceType]
COLOR_UNSPECIFIED: Color
COLOR_WHITE: Color
COLOR_BLACK: Color
PIECE_TYPE_UNSPECIFIED: PieceType
PIECE_TYPE_PAWN: PieceType
PIECE_TYPE_KNIGHT: PieceType
PIECE_TYPE_BISHOP: PieceType
PIECE_TYPE_ROOK: PieceType
PIECE_TYPE_QUEEN: PieceType
PIECE_TYPE_KING: PieceType

class Occupant(_message.Message):
    __slots__ = ("color", "piece_type")
    COLOR_FIELD_NUMBER: _ClassVar[int]
    PIECE_TYPE_FIELD_NUMBER: _ClassVar[int]
    color: Color
    piece_type: PieceType
    def __init__(self, color: _Optional[_Union[Color, str]] = ..., piece_type: _Optional[_Union[PieceType, str]] = ...) -> None: ...
