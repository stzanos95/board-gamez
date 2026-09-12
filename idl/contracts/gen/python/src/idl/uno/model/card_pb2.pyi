from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CardColor(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CARD_COLOR_UNSPECIFIED: _ClassVar[CardColor]
    CARD_COLOR_RED: _ClassVar[CardColor]
    CARD_COLOR_YELLOW: _ClassVar[CardColor]
    CARD_COLOR_GREEN: _ClassVar[CardColor]
    CARD_COLOR_BLUE: _ClassVar[CardColor]

class CardKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CARD_KIND_UNSPECIFIED: _ClassVar[CardKind]
    CARD_KIND_NUMBER: _ClassVar[CardKind]
    CARD_KIND_SKIP: _ClassVar[CardKind]
    CARD_KIND_REVERSE: _ClassVar[CardKind]
    CARD_KIND_DRAW_TWO: _ClassVar[CardKind]
    CARD_KIND_WILD: _ClassVar[CardKind]
    CARD_KIND_WILD_DRAW_FOUR: _ClassVar[CardKind]
CARD_COLOR_UNSPECIFIED: CardColor
CARD_COLOR_RED: CardColor
CARD_COLOR_YELLOW: CardColor
CARD_COLOR_GREEN: CardColor
CARD_COLOR_BLUE: CardColor
CARD_KIND_UNSPECIFIED: CardKind
CARD_KIND_NUMBER: CardKind
CARD_KIND_SKIP: CardKind
CARD_KIND_REVERSE: CardKind
CARD_KIND_DRAW_TWO: CardKind
CARD_KIND_WILD: CardKind
CARD_KIND_WILD_DRAW_FOUR: CardKind

class Card(_message.Message):
    __slots__ = ("kind", "color", "number")
    KIND_FIELD_NUMBER: _ClassVar[int]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    kind: CardKind
    color: CardColor
    number: int
    def __init__(self, kind: _Optional[_Union[CardKind, str]] = ..., color: _Optional[_Union[CardColor, str]] = ..., number: _Optional[int] = ...) -> None: ...
