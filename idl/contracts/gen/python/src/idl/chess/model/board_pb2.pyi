from idl.chess.model import castling_pb2 as _castling_pb2
from idl.chess.model import piece_pb2 as _piece_pb2
from idl.chess.model import square_pb2 as _square_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SquareOccupant(_message.Message):
    __slots__ = ("square", "occupant")
    SQUARE_FIELD_NUMBER: _ClassVar[int]
    OCCUPANT_FIELD_NUMBER: _ClassVar[int]
    square: _square_pb2.Square
    occupant: _piece_pb2.Occupant
    def __init__(self, square: _Optional[_Union[_square_pb2.Square, _Mapping]] = ..., occupant: _Optional[_Union[_piece_pb2.Occupant, _Mapping]] = ...) -> None: ...

class BoardState(_message.Message):
    __slots__ = ("occupancy", "side_to_move", "castling_rights", "en_passant_target", "halfmove_clock", "fullmove_number")
    OCCUPANCY_FIELD_NUMBER: _ClassVar[int]
    SIDE_TO_MOVE_FIELD_NUMBER: _ClassVar[int]
    CASTLING_RIGHTS_FIELD_NUMBER: _ClassVar[int]
    EN_PASSANT_TARGET_FIELD_NUMBER: _ClassVar[int]
    HALFMOVE_CLOCK_FIELD_NUMBER: _ClassVar[int]
    FULLMOVE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    occupancy: _containers.RepeatedCompositeFieldContainer[SquareOccupant]
    side_to_move: _piece_pb2.Color
    castling_rights: _castling_pb2.CastlingRights
    en_passant_target: _square_pb2.Square
    halfmove_clock: int
    fullmove_number: int
    def __init__(self, occupancy: _Optional[_Iterable[_Union[SquareOccupant, _Mapping]]] = ..., side_to_move: _Optional[_Union[_piece_pb2.Color, str]] = ..., castling_rights: _Optional[_Union[_castling_pb2.CastlingRights, _Mapping]] = ..., en_passant_target: _Optional[_Union[_square_pb2.Square, _Mapping]] = ..., halfmove_clock: _Optional[int] = ..., fullmove_number: _Optional[int] = ...) -> None: ...

class PositionKey(_message.Message):
    __slots__ = ("occupancy", "side_to_move", "castling_rights", "en_passant_target")
    OCCUPANCY_FIELD_NUMBER: _ClassVar[int]
    SIDE_TO_MOVE_FIELD_NUMBER: _ClassVar[int]
    CASTLING_RIGHTS_FIELD_NUMBER: _ClassVar[int]
    EN_PASSANT_TARGET_FIELD_NUMBER: _ClassVar[int]
    occupancy: _containers.RepeatedCompositeFieldContainer[SquareOccupant]
    side_to_move: _piece_pb2.Color
    castling_rights: _castling_pb2.CastlingRights
    en_passant_target: _square_pb2.Square
    def __init__(self, occupancy: _Optional[_Iterable[_Union[SquareOccupant, _Mapping]]] = ..., side_to_move: _Optional[_Union[_piece_pb2.Color, str]] = ..., castling_rights: _Optional[_Union[_castling_pb2.CastlingRights, _Mapping]] = ..., en_passant_target: _Optional[_Union[_square_pb2.Square, _Mapping]] = ...) -> None: ...
