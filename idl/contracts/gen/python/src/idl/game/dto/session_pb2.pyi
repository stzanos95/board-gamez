from idl.game.model import game_type_pb2 as _game_type_pb2
from idl.game.model import participant_pb2 as _participant_pb2
from idl.game.model import session_pb2 as _session_pb2
from idl.game.model import withdrawal_result_pb2 as _withdrawal_result_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateSessionRequest(_message.Message):
    __slots__ = ("table_id", "player_id", "game_type", "participants")
    TABLE_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    GAME_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANTS_FIELD_NUMBER: _ClassVar[int]
    table_id: str
    player_id: str
    game_type: _game_type_pb2.GameType
    participants: _containers.RepeatedCompositeFieldContainer[_participant_pb2.Participant]
    def __init__(self, table_id: _Optional[str] = ..., player_id: _Optional[str] = ..., game_type: _Optional[_Union[_game_type_pb2.GameType, str]] = ..., participants: _Optional[_Iterable[_Union[_participant_pb2.Participant, _Mapping]]] = ...) -> None: ...

class CreateSessionResponse(_message.Message):
    __slots__ = ("session",)
    SESSION_FIELD_NUMBER: _ClassVar[int]
    session: _session_pb2.SessionView
    def __init__(self, session: _Optional[_Union[_session_pb2.SessionView, _Mapping]] = ...) -> None: ...

class ReadSessionRequest(_message.Message):
    __slots__ = ("session_id", "player_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    player_id: str
    def __init__(self, session_id: _Optional[str] = ..., player_id: _Optional[str] = ...) -> None: ...

class ReadSessionResponse(_message.Message):
    __slots__ = ("session",)
    SESSION_FIELD_NUMBER: _ClassVar[int]
    session: _session_pb2.SessionView
    def __init__(self, session: _Optional[_Union[_session_pb2.SessionView, _Mapping]] = ...) -> None: ...

class WithdrawPlayerRequest(_message.Message):
    __slots__ = ("session_id", "player_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    player_id: str
    def __init__(self, session_id: _Optional[str] = ..., player_id: _Optional[str] = ...) -> None: ...

class WithdrawPlayerResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _withdrawal_result_pb2.WithdrawalResult
    def __init__(self, result: _Optional[_Union[_withdrawal_result_pb2.WithdrawalResult, _Mapping]] = ...) -> None: ...
