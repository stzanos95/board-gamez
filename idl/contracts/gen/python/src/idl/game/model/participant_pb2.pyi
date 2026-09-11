from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Participant(_message.Message):
    __slots__ = ("number", "player_id")
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    number: int
    player_id: str
    def __init__(self, number: _Optional[int] = ..., player_id: _Optional[str] = ...) -> None: ...
