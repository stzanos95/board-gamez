from idl.uno.model import card_pb2 as _card_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CardPlay(_message.Message):
    __slots__ = ("card", "chosen_color")
    CARD_FIELD_NUMBER: _ClassVar[int]
    CHOSEN_COLOR_FIELD_NUMBER: _ClassVar[int]
    card: _card_pb2.Card
    chosen_color: _card_pb2.CardColor
    def __init__(self, card: _Optional[_Union[_card_pb2.Card, _Mapping]] = ..., chosen_color: _Optional[_Union[_card_pb2.CardColor, str]] = ...) -> None: ...

class CardDraw(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TurnPass(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UnoAction(_message.Message):
    __slots__ = ("play", "draw")
    PLAY_FIELD_NUMBER: _ClassVar[int]
    DRAW_FIELD_NUMBER: _ClassVar[int]
    PASS_FIELD_NUMBER: _ClassVar[int]
    play: CardPlay
    draw: CardDraw
    def __init__(self, play: _Optional[_Union[CardPlay, _Mapping]] = ..., draw: _Optional[_Union[CardDraw, _Mapping]] = ..., **kwargs) -> None: ...
