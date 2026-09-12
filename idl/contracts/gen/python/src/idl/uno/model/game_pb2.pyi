from idl.uno.model import card_pb2 as _card_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PlayDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PLAY_DIRECTION_UNSPECIFIED: _ClassVar[PlayDirection]
    PLAY_DIRECTION_CLOCKWISE: _ClassVar[PlayDirection]
    PLAY_DIRECTION_COUNTERCLOCKWISE: _ClassVar[PlayDirection]

class UnoResultReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNO_RESULT_REASON_UNSPECIFIED: _ClassVar[UnoResultReason]
    UNO_RESULT_REASON_HAND_EMPTIED: _ClassVar[UnoResultReason]
    UNO_RESULT_REASON_OTHERS_WITHDREW: _ClassVar[UnoResultReason]
PLAY_DIRECTION_UNSPECIFIED: PlayDirection
PLAY_DIRECTION_CLOCKWISE: PlayDirection
PLAY_DIRECTION_COUNTERCLOCKWISE: PlayDirection
UNO_RESULT_REASON_UNSPECIFIED: UnoResultReason
UNO_RESULT_REASON_HAND_EMPTIED: UnoResultReason
UNO_RESULT_REASON_OTHERS_WITHDREW: UnoResultReason

class UnoHand(_message.Message):
    __slots__ = ("participant", "cards", "has_withdrawn")
    PARTICIPANT_FIELD_NUMBER: _ClassVar[int]
    CARDS_FIELD_NUMBER: _ClassVar[int]
    HAS_WITHDRAWN_FIELD_NUMBER: _ClassVar[int]
    participant: int
    cards: _containers.RepeatedCompositeFieldContainer[_card_pb2.Card]
    has_withdrawn: bool
    def __init__(self, participant: _Optional[int] = ..., cards: _Optional[_Iterable[_Union[_card_pb2.Card, _Mapping]]] = ..., has_withdrawn: bool = ...) -> None: ...

class UnoResult(_message.Message):
    __slots__ = ("winner", "reason")
    WINNER_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    winner: int
    reason: UnoResultReason
    def __init__(self, winner: _Optional[int] = ..., reason: _Optional[_Union[UnoResultReason, str]] = ...) -> None: ...

class UnoGame(_message.Message):
    __slots__ = ("hands", "draw_pile", "discard_pile", "active_color", "direction", "participant_to_act", "drawn_card", "seed", "shuffle_count", "result")
    HANDS_FIELD_NUMBER: _ClassVar[int]
    DRAW_PILE_FIELD_NUMBER: _ClassVar[int]
    DISCARD_PILE_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_COLOR_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_TO_ACT_FIELD_NUMBER: _ClassVar[int]
    DRAWN_CARD_FIELD_NUMBER: _ClassVar[int]
    SEED_FIELD_NUMBER: _ClassVar[int]
    SHUFFLE_COUNT_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    hands: _containers.RepeatedCompositeFieldContainer[UnoHand]
    draw_pile: _containers.RepeatedCompositeFieldContainer[_card_pb2.Card]
    discard_pile: _containers.RepeatedCompositeFieldContainer[_card_pb2.Card]
    active_color: _card_pb2.CardColor
    direction: PlayDirection
    participant_to_act: int
    drawn_card: _card_pb2.Card
    seed: int
    shuffle_count: int
    result: UnoResult
    def __init__(self, hands: _Optional[_Iterable[_Union[UnoHand, _Mapping]]] = ..., draw_pile: _Optional[_Iterable[_Union[_card_pb2.Card, _Mapping]]] = ..., discard_pile: _Optional[_Iterable[_Union[_card_pb2.Card, _Mapping]]] = ..., active_color: _Optional[_Union[_card_pb2.CardColor, str]] = ..., direction: _Optional[_Union[PlayDirection, str]] = ..., participant_to_act: _Optional[int] = ..., drawn_card: _Optional[_Union[_card_pb2.Card, _Mapping]] = ..., seed: _Optional[int] = ..., shuffle_count: _Optional[int] = ..., result: _Optional[_Union[UnoResult, _Mapping]] = ...) -> None: ...
