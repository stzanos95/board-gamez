from google.protobuf import timestamp_pb2 as _timestamp_pb2
from idl.core.obj import object_metadata_pb2 as _object_metadata_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DeadlineObj(_message.Message):
    __slots__ = ("metadata", "acts_by", "session_version")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    ACTS_BY_FIELD_NUMBER: _ClassVar[int]
    SESSION_VERSION_FIELD_NUMBER: _ClassVar[int]
    metadata: _object_metadata_pb2.ObjectMetadata
    acts_by: _timestamp_pb2.Timestamp
    session_version: int
    def __init__(self, metadata: _Optional[_Union[_object_metadata_pb2.ObjectMetadata, _Mapping]] = ..., acts_by: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., session_version: _Optional[int] = ...) -> None: ...
