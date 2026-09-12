from google.protobuf import any_pb2 as _any_pb2
from idl.game.model import action_pb2 as _action_pb2
from idl.game.model import game_spec_pb2 as _game_spec_pb2
from idl.game.model import game_state_pb2 as _game_state_pb2
from idl.game.model import participant_pb2 as _participant_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateGameRequest(_message.Message):
    __slots__ = ("participant_count", "participant_roles", "seed")
    PARTICIPANT_COUNT_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_ROLES_FIELD_NUMBER: _ClassVar[int]
    SEED_FIELD_NUMBER: _ClassVar[int]
    participant_count: int
    participant_roles: _containers.RepeatedCompositeFieldContainer[_participant_pb2.ParticipantRole]
    seed: int
    def __init__(self, participant_count: _Optional[int] = ..., participant_roles: _Optional[_Iterable[_Union[_participant_pb2.ParticipantRole, _Mapping]]] = ..., seed: _Optional[int] = ...) -> None: ...

class CreateGameResponse(_message.Message):
    __slots__ = ("state",)
    STATE_FIELD_NUMBER: _ClassVar[int]
    state: _game_state_pb2.GameState
    def __init__(self, state: _Optional[_Union[_game_state_pb2.GameState, _Mapping]] = ...) -> None: ...

class ApplyActionRequest(_message.Message):
    __slots__ = ("state", "action")
    STATE_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    state: _game_state_pb2.GameState
    action: _action_pb2.Action
    def __init__(self, state: _Optional[_Union[_game_state_pb2.GameState, _Mapping]] = ..., action: _Optional[_Union[_action_pb2.Action, _Mapping]] = ...) -> None: ...

class ApplyActionResponse(_message.Message):
    __slots__ = ("state",)
    STATE_FIELD_NUMBER: _ClassVar[int]
    state: _game_state_pb2.GameState
    def __init__(self, state: _Optional[_Union[_game_state_pb2.GameState, _Mapping]] = ...) -> None: ...

class ReadViewRequest(_message.Message):
    __slots__ = ("state", "participant")
    STATE_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_FIELD_NUMBER: _ClassVar[int]
    state: _game_state_pb2.GameState
    participant: int
    def __init__(self, state: _Optional[_Union[_game_state_pb2.GameState, _Mapping]] = ..., participant: _Optional[int] = ...) -> None: ...

class ReadViewResponse(_message.Message):
    __slots__ = ("view",)
    VIEW_FIELD_NUMBER: _ClassVar[int]
    view: _any_pb2.Any
    def __init__(self, view: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class WithdrawParticipantRequest(_message.Message):
    __slots__ = ("state", "participant")
    STATE_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_FIELD_NUMBER: _ClassVar[int]
    state: _game_state_pb2.GameState
    participant: int
    def __init__(self, state: _Optional[_Union[_game_state_pb2.GameState, _Mapping]] = ..., participant: _Optional[int] = ...) -> None: ...

class WithdrawParticipantResponse(_message.Message):
    __slots__ = ("state",)
    STATE_FIELD_NUMBER: _ClassVar[int]
    state: _game_state_pb2.GameState
    def __init__(self, state: _Optional[_Union[_game_state_pb2.GameState, _Mapping]] = ...) -> None: ...

class ExpireDeadlineRequest(_message.Message):
    __slots__ = ("state",)
    STATE_FIELD_NUMBER: _ClassVar[int]
    state: _game_state_pb2.GameState
    def __init__(self, state: _Optional[_Union[_game_state_pb2.GameState, _Mapping]] = ...) -> None: ...

class ExpireDeadlineResponse(_message.Message):
    __slots__ = ("state",)
    STATE_FIELD_NUMBER: _ClassVar[int]
    state: _game_state_pb2.GameState
    def __init__(self, state: _Optional[_Union[_game_state_pb2.GameState, _Mapping]] = ...) -> None: ...

class ReadBoundsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ReadBoundsResponse(_message.Message):
    __slots__ = ("bounds",)
    BOUNDS_FIELD_NUMBER: _ClassVar[int]
    bounds: _game_spec_pb2.ParticipantBounds
    def __init__(self, bounds: _Optional[_Union[_game_spec_pb2.ParticipantBounds, _Mapping]] = ...) -> None: ...
