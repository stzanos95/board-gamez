from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class GameType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GAME_TYPE_UNSPECIFIED: _ClassVar[GameType]
    GAME_TYPE_CHESS: _ClassVar[GameType]
GAME_TYPE_UNSPECIFIED: GameType
GAME_TYPE_CHESS: GameType
