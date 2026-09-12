from idl.uno.model import card_pb2 as _card_pb2
from idl.uno.model import game_pb2 as _game_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HandCard(_message.Message):
    __slots__ = ("card", "is_playable")
    CARD_FIELD_NUMBER: _ClassVar[int]
    IS_PLAYABLE_FIELD_NUMBER: _ClassVar[int]
    card: _card_pb2.Card
    is_playable: bool
    def __init__(self, card: _Optional[_Union[_card_pb2.Card, _Mapping]] = ..., is_playable: bool = ...) -> None: ...

class UnoPlayerSummary(_message.Message):
    __slots__ = ("participant", "card_count", "has_withdrawn")
    PARTICIPANT_FIELD_NUMBER: _ClassVar[int]
    CARD_COUNT_FIELD_NUMBER: _ClassVar[int]
    HAS_WITHDRAWN_FIELD_NUMBER: _ClassVar[int]
    participant: int
    card_count: int
    has_withdrawn: bool
    def __init__(self, participant: _Optional[int] = ..., card_count: _Optional[int] = ..., has_withdrawn: bool = ...) -> None: ...

class UnoView(_message.Message):
    __slots__ = ("players", "hand", "top_card", "active_color", "direction", "participant_to_act", "draw_pile_count", "may_draw", "may_pass", "drawn_card", "result")
    PLAYERS_FIELD_NUMBER: _ClassVar[int]
    HAND_FIELD_NUMBER: _ClassVar[int]
    TOP_CARD_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_COLOR_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_TO_ACT_FIELD_NUMBER: _ClassVar[int]
    DRAW_PILE_COUNT_FIELD_NUMBER: _ClassVar[int]
    MAY_DRAW_FIELD_NUMBER: _ClassVar[int]
    MAY_PASS_FIELD_NUMBER: _ClassVar[int]
    DRAWN_CARD_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    players: _containers.RepeatedCompositeFieldContainer[UnoPlayerSummary]
    hand: _containers.RepeatedCompositeFieldContainer[HandCard]
    top_card: _card_pb2.Card
    active_color: _card_pb2.CardColor
    direction: _game_pb2.PlayDirection
    participant_to_act: int
    draw_pile_count: int
    may_draw: bool
    may_pass: bool
    drawn_card: _card_pb2.Card
    result: _game_pb2.UnoResult
    def __init__(self, players: _Optional[_Iterable[_Union[UnoPlayerSummary, _Mapping]]] = ..., hand: _Optional[_Iterable[_Union[HandCard, _Mapping]]] = ..., top_card: _Optional[_Union[_card_pb2.Card, _Mapping]] = ..., active_color: _Optional[_Union[_card_pb2.CardColor, str]] = ..., direction: _Optional[_Union[_game_pb2.PlayDirection, str]] = ..., participant_to_act: _Optional[int] = ..., draw_pile_count: _Optional[int] = ..., may_draw: bool = ..., may_pass: bool = ..., drawn_card: _Optional[_Union[_card_pb2.Card, _Mapping]] = ..., result: _Optional[_Union[_game_pb2.UnoResult, _Mapping]] = ...) -> None: ...
