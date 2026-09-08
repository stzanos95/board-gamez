from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class File(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FILE_UNSPECIFIED: _ClassVar[File]
    FILE_A: _ClassVar[File]
    FILE_B: _ClassVar[File]
    FILE_C: _ClassVar[File]
    FILE_D: _ClassVar[File]
    FILE_E: _ClassVar[File]
    FILE_F: _ClassVar[File]
    FILE_G: _ClassVar[File]
    FILE_H: _ClassVar[File]

class Rank(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RANK_UNSPECIFIED: _ClassVar[Rank]
    RANK_1: _ClassVar[Rank]
    RANK_2: _ClassVar[Rank]
    RANK_3: _ClassVar[Rank]
    RANK_4: _ClassVar[Rank]
    RANK_5: _ClassVar[Rank]
    RANK_6: _ClassVar[Rank]
    RANK_7: _ClassVar[Rank]
    RANK_8: _ClassVar[Rank]
FILE_UNSPECIFIED: File
FILE_A: File
FILE_B: File
FILE_C: File
FILE_D: File
FILE_E: File
FILE_F: File
FILE_G: File
FILE_H: File
RANK_UNSPECIFIED: Rank
RANK_1: Rank
RANK_2: Rank
RANK_3: Rank
RANK_4: Rank
RANK_5: Rank
RANK_6: Rank
RANK_7: Rank
RANK_8: Rank

class Square(_message.Message):
    __slots__ = ("file", "rank")
    FILE_FIELD_NUMBER: _ClassVar[int]
    RANK_FIELD_NUMBER: _ClassVar[int]
    file: File
    rank: Rank
    def __init__(self, file: _Optional[_Union[File, str]] = ..., rank: _Optional[_Union[Rank, str]] = ...) -> None: ...
