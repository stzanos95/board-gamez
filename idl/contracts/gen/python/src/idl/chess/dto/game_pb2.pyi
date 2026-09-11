from idl.chess.model import action_pb2 as _action_pb2
from idl.chess.model import session_pb2 as _session_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StartGameRequest(_message.Message):
    __slots__ = ("table_id", "player_id")
    TABLE_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    table_id: str
    player_id: str
    def __init__(self, table_id: _Optional[str] = ..., player_id: _Optional[str] = ...) -> None: ...

class StartGameResponse(_message.Message):
    __slots__ = ("session",)
    SESSION_FIELD_NUMBER: _ClassVar[int]
    session: _session_pb2.ChessSession
    def __init__(self, session: _Optional[_Union[_session_pb2.ChessSession, _Mapping]] = ...) -> None: ...

class ReadGameRequest(_message.Message):
    __slots__ = ("table_id", "player_id")
    TABLE_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    table_id: str
    player_id: str
    def __init__(self, table_id: _Optional[str] = ..., player_id: _Optional[str] = ...) -> None: ...

class ReadGameResponse(_message.Message):
    __slots__ = ("session",)
    SESSION_FIELD_NUMBER: _ClassVar[int]
    session: _session_pb2.ChessSession
    def __init__(self, session: _Optional[_Union[_session_pb2.ChessSession, _Mapping]] = ...) -> None: ...

class PlayActionRequest(_message.Message):
    __slots__ = ("table_id", "command_id", "player_id", "action", "expected_version")
    TABLE_ID_FIELD_NUMBER: _ClassVar[int]
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_VERSION_FIELD_NUMBER: _ClassVar[int]
    table_id: str
    command_id: str
    player_id: str
    action: _action_pb2.ChessAction
    expected_version: int
    def __init__(self, table_id: _Optional[str] = ..., command_id: _Optional[str] = ..., player_id: _Optional[str] = ..., action: _Optional[_Union[_action_pb2.ChessAction, _Mapping]] = ..., expected_version: _Optional[int] = ...) -> None: ...

class PlayActionResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _session_pb2.ActionResult
    def __init__(self, result: _Optional[_Union[_session_pb2.ActionResult, _Mapping]] = ...) -> None: ...
