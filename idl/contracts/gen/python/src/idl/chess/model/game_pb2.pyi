from idl.chess.model import board_pb2 as _board_pb2
from idl.chess.model import move_pb2 as _move_pb2
from idl.chess.model import piece_pb2 as _piece_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GameStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GAME_STATUS_UNSPECIFIED: _ClassVar[GameStatus]
    GAME_STATUS_IN_PROGRESS: _ClassVar[GameStatus]
    GAME_STATUS_CHECK: _ClassVar[GameStatus]
    GAME_STATUS_CHECKMATE: _ClassVar[GameStatus]
    GAME_STATUS_STALEMATE: _ClassVar[GameStatus]
    GAME_STATUS_DRAW_BY_FIFTY_MOVE_RULE: _ClassVar[GameStatus]
    GAME_STATUS_DRAW_BY_REPETITION: _ClassVar[GameStatus]
    GAME_STATUS_DRAW_BY_INSUFFICIENT_MATERIAL: _ClassVar[GameStatus]

class GameOutcome(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GAME_OUTCOME_UNSPECIFIED: _ClassVar[GameOutcome]
    GAME_OUTCOME_WHITE_WINS: _ClassVar[GameOutcome]
    GAME_OUTCOME_BLACK_WINS: _ClassVar[GameOutcome]
    GAME_OUTCOME_DRAW: _ClassVar[GameOutcome]
GAME_STATUS_UNSPECIFIED: GameStatus
GAME_STATUS_IN_PROGRESS: GameStatus
GAME_STATUS_CHECK: GameStatus
GAME_STATUS_CHECKMATE: GameStatus
GAME_STATUS_STALEMATE: GameStatus
GAME_STATUS_DRAW_BY_FIFTY_MOVE_RULE: GameStatus
GAME_STATUS_DRAW_BY_REPETITION: GameStatus
GAME_STATUS_DRAW_BY_INSUFFICIENT_MATERIAL: GameStatus
GAME_OUTCOME_UNSPECIFIED: GameOutcome
GAME_OUTCOME_WHITE_WINS: GameOutcome
GAME_OUTCOME_BLACK_WINS: GameOutcome
GAME_OUTCOME_DRAW: GameOutcome

class ChessPlayer(_message.Message):
    __slots__ = ("name", "color")
    NAME_FIELD_NUMBER: _ClassVar[int]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    name: str
    color: _piece_pb2.Color
    def __init__(self, name: _Optional[str] = ..., color: _Optional[_Union[_piece_pb2.Color, str]] = ...) -> None: ...

class PlayerRoster(_message.Message):
    __slots__ = ("white", "black")
    WHITE_FIELD_NUMBER: _ClassVar[int]
    BLACK_FIELD_NUMBER: _ClassVar[int]
    white: ChessPlayer
    black: ChessPlayer
    def __init__(self, white: _Optional[_Union[ChessPlayer, _Mapping]] = ..., black: _Optional[_Union[ChessPlayer, _Mapping]] = ...) -> None: ...

class ChessTurn(_message.Message):
    __slots__ = ("number", "player", "move", "notation", "resulting_status")
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    PLAYER_FIELD_NUMBER: _ClassVar[int]
    MOVE_FIELD_NUMBER: _ClassVar[int]
    NOTATION_FIELD_NUMBER: _ClassVar[int]
    RESULTING_STATUS_FIELD_NUMBER: _ClassVar[int]
    number: int
    player: ChessPlayer
    move: _move_pb2.Move
    notation: str
    resulting_status: GameStatus
    def __init__(self, number: _Optional[int] = ..., player: _Optional[_Union[ChessPlayer, _Mapping]] = ..., move: _Optional[_Union[_move_pb2.Move, _Mapping]] = ..., notation: _Optional[str] = ..., resulting_status: _Optional[_Union[GameStatus, str]] = ...) -> None: ...

class ChessTurnHistory(_message.Message):
    __slots__ = ("turns", "position_keys")
    TURNS_FIELD_NUMBER: _ClassVar[int]
    POSITION_KEYS_FIELD_NUMBER: _ClassVar[int]
    turns: _containers.RepeatedCompositeFieldContainer[ChessTurn]
    position_keys: _containers.RepeatedCompositeFieldContainer[_board_pb2.PositionKey]
    def __init__(self, turns: _Optional[_Iterable[_Union[ChessTurn, _Mapping]]] = ..., position_keys: _Optional[_Iterable[_Union[_board_pb2.PositionKey, _Mapping]]] = ...) -> None: ...

class GameResult(_message.Message):
    __slots__ = ("outcome", "winner", "status", "resigning_player")
    OUTCOME_FIELD_NUMBER: _ClassVar[int]
    WINNER_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RESIGNING_PLAYER_FIELD_NUMBER: _ClassVar[int]
    outcome: GameOutcome
    winner: ChessPlayer
    status: GameStatus
    resigning_player: ChessPlayer
    def __init__(self, outcome: _Optional[_Union[GameOutcome, str]] = ..., winner: _Optional[_Union[ChessPlayer, _Mapping]] = ..., status: _Optional[_Union[GameStatus, str]] = ..., resigning_player: _Optional[_Union[ChessPlayer, _Mapping]] = ...) -> None: ...

class ChessGame(_message.Message):
    __slots__ = ("roster", "state", "history", "legal_moves", "status", "resigning_color", "result")
    ROSTER_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    HISTORY_FIELD_NUMBER: _ClassVar[int]
    LEGAL_MOVES_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RESIGNING_COLOR_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    roster: PlayerRoster
    state: _board_pb2.BoardState
    history: ChessTurnHistory
    legal_moves: _containers.RepeatedCompositeFieldContainer[_move_pb2.Move]
    status: GameStatus
    resigning_color: _piece_pb2.Color
    result: GameResult
    def __init__(self, roster: _Optional[_Union[PlayerRoster, _Mapping]] = ..., state: _Optional[_Union[_board_pb2.BoardState, _Mapping]] = ..., history: _Optional[_Union[ChessTurnHistory, _Mapping]] = ..., legal_moves: _Optional[_Iterable[_Union[_move_pb2.Move, _Mapping]]] = ..., status: _Optional[_Union[GameStatus, str]] = ..., resigning_color: _Optional[_Union[_piece_pb2.Color, str]] = ..., result: _Optional[_Union[GameResult, _Mapping]] = ...) -> None: ...
