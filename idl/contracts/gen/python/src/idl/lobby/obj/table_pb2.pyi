from idl.core.obj import object_metadata_pb2 as _object_metadata_pb2
from idl.game.model import game_type_pb2 as _game_type_pb2
from idl.lobby.model import seat_pb2 as _seat_pb2
from idl.lobby.model import table_pb2 as _table_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TableObj(_message.Message):
    __slots__ = ("metadata", "game_type", "status", "seats", "player_ids")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    GAME_TYPE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SEATS_FIELD_NUMBER: _ClassVar[int]
    PLAYER_IDS_FIELD_NUMBER: _ClassVar[int]
    metadata: _object_metadata_pb2.ObjectMetadata
    game_type: _game_type_pb2.GameType
    status: _table_pb2.TableStatus
    seats: _containers.RepeatedCompositeFieldContainer[_seat_pb2.Seat]
    player_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, metadata: _Optional[_Union[_object_metadata_pb2.ObjectMetadata, _Mapping]] = ..., game_type: _Optional[_Union[_game_type_pb2.GameType, str]] = ..., status: _Optional[_Union[_table_pb2.TableStatus, str]] = ..., seats: _Optional[_Iterable[_Union[_seat_pb2.Seat, _Mapping]]] = ..., player_ids: _Optional[_Iterable[str]] = ...) -> None: ...
