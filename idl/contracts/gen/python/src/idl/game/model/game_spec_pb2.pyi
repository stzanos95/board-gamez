from idl.game.model import game_type_pb2 as _game_type_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ParticipantBounds(_message.Message):
    __slots__ = ("minimum", "maximum")
    MINIMUM_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_FIELD_NUMBER: _ClassVar[int]
    minimum: int
    maximum: int
    def __init__(self, minimum: _Optional[int] = ..., maximum: _Optional[int] = ...) -> None: ...

class GameSpec(_message.Message):
    __slots__ = ("game_type", "bounds")
    GAME_TYPE_FIELD_NUMBER: _ClassVar[int]
    BOUNDS_FIELD_NUMBER: _ClassVar[int]
    game_type: _game_type_pb2.GameType
    bounds: ParticipantBounds
    def __init__(self, game_type: _Optional[_Union[_game_type_pb2.GameType, str]] = ..., bounds: _Optional[_Union[ParticipantBounds, _Mapping]] = ...) -> None: ...

class GameSpecCollection(_message.Message):
    __slots__ = ("game_spec_items",)
    GAME_SPEC_ITEMS_FIELD_NUMBER: _ClassVar[int]
    game_spec_items: _containers.RepeatedCompositeFieldContainer[GameSpec]
    def __init__(self, game_spec_items: _Optional[_Iterable[_Union[GameSpec, _Mapping]]] = ...) -> None: ...
