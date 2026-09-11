from idl.game.model import game_spec_pb2 as _game_spec_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListGameSpecRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListGameSpecResponse(_message.Message):
    __slots__ = ("collection",)
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    collection: _game_spec_pb2.GameSpecCollection
    def __init__(self, collection: _Optional[_Union[_game_spec_pb2.GameSpecCollection, _Mapping]] = ...) -> None: ...
