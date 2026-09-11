from idl.chess.model import game_pb2 as _game_pb2
from idl.chess.model import piece_pb2 as _piece_pb2
from idl.game.model import command_result_pb2 as _command_result_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ChessSession(_message.Message):
    __slots__ = ("id", "game", "color", "last_command_id", "version")
    ID_FIELD_NUMBER: _ClassVar[int]
    GAME_FIELD_NUMBER: _ClassVar[int]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    LAST_COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    id: str
    game: _game_pb2.ChessGame
    color: _piece_pb2.Color
    last_command_id: str
    version: int
    def __init__(self, id: _Optional[str] = ..., game: _Optional[_Union[_game_pb2.ChessGame, _Mapping]] = ..., color: _Optional[_Union[_piece_pb2.Color, str]] = ..., last_command_id: _Optional[str] = ..., version: _Optional[int] = ...) -> None: ...

class ActionResult(_message.Message):
    __slots__ = ("outcome", "session")
    OUTCOME_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    outcome: _command_result_pb2.CommandOutcome
    session: ChessSession
    def __init__(self, outcome: _Optional[_Union[_command_result_pb2.CommandOutcome, str]] = ..., session: _Optional[_Union[ChessSession, _Mapping]] = ...) -> None: ...
