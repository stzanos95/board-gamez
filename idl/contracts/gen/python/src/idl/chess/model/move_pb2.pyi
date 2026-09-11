from idl.chess.model import castling_pb2 as _castling_pb2
from idl.chess.model import piece_pb2 as _piece_pb2
from idl.chess.model import square_pb2 as _square_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MoveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MOVE_TYPE_UNSPECIFIED: _ClassVar[MoveType]
    MOVE_TYPE_QUIET: _ClassVar[MoveType]
    MOVE_TYPE_CAPTURE: _ClassVar[MoveType]
    MOVE_TYPE_DOUBLE_PAWN_PUSH: _ClassVar[MoveType]
    MOVE_TYPE_EN_PASSANT: _ClassVar[MoveType]
    MOVE_TYPE_CASTLE: _ClassVar[MoveType]
    MOVE_TYPE_PROMOTION: _ClassVar[MoveType]
    MOVE_TYPE_PROMOTION_CAPTURE: _ClassVar[MoveType]
MOVE_TYPE_UNSPECIFIED: MoveType
MOVE_TYPE_QUIET: MoveType
MOVE_TYPE_CAPTURE: MoveType
MOVE_TYPE_DOUBLE_PAWN_PUSH: MoveType
MOVE_TYPE_EN_PASSANT: MoveType
MOVE_TYPE_CASTLE: MoveType
MOVE_TYPE_PROMOTION: MoveType
MOVE_TYPE_PROMOTION_CAPTURE: MoveType

class CoordinateMove(_message.Message):
    __slots__ = ("origin", "destination", "promotion_type")
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_FIELD_NUMBER: _ClassVar[int]
    PROMOTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    origin: _square_pb2.Square
    destination: _square_pb2.Square
    promotion_type: _piece_pb2.PieceType
    def __init__(self, origin: _Optional[_Union[_square_pb2.Square, _Mapping]] = ..., destination: _Optional[_Union[_square_pb2.Square, _Mapping]] = ..., promotion_type: _Optional[_Union[_piece_pb2.PieceType, str]] = ...) -> None: ...

class Move(_message.Message):
    __slots__ = ("origin", "destination", "moving_color", "moving_piece_type", "move_type", "captured_square", "promotion_type", "castling_side", "rook_origin", "rook_destination")
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_FIELD_NUMBER: _ClassVar[int]
    MOVING_COLOR_FIELD_NUMBER: _ClassVar[int]
    MOVING_PIECE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MOVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    CAPTURED_SQUARE_FIELD_NUMBER: _ClassVar[int]
    PROMOTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    CASTLING_SIDE_FIELD_NUMBER: _ClassVar[int]
    ROOK_ORIGIN_FIELD_NUMBER: _ClassVar[int]
    ROOK_DESTINATION_FIELD_NUMBER: _ClassVar[int]
    origin: _square_pb2.Square
    destination: _square_pb2.Square
    moving_color: _piece_pb2.Color
    moving_piece_type: _piece_pb2.PieceType
    move_type: MoveType
    captured_square: _square_pb2.Square
    promotion_type: _piece_pb2.PieceType
    castling_side: _castling_pb2.CastlingSide
    rook_origin: _square_pb2.Square
    rook_destination: _square_pb2.Square
    def __init__(self, origin: _Optional[_Union[_square_pb2.Square, _Mapping]] = ..., destination: _Optional[_Union[_square_pb2.Square, _Mapping]] = ..., moving_color: _Optional[_Union[_piece_pb2.Color, str]] = ..., moving_piece_type: _Optional[_Union[_piece_pb2.PieceType, str]] = ..., move_type: _Optional[_Union[MoveType, str]] = ..., captured_square: _Optional[_Union[_square_pb2.Square, _Mapping]] = ..., promotion_type: _Optional[_Union[_piece_pb2.PieceType, str]] = ..., castling_side: _Optional[_Union[_castling_pb2.CastlingSide, str]] = ..., rook_origin: _Optional[_Union[_square_pb2.Square, _Mapping]] = ..., rook_destination: _Optional[_Union[_square_pb2.Square, _Mapping]] = ...) -> None: ...
