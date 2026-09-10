"""
Working with protobuf messages, where the work is not any one domain's.
"""

from typing import TypeVar

from google.protobuf.json_format import MessageToDict, ParseDict
from google.protobuf.message import Message
from pydantic import BaseModel

MessageT = TypeVar("MessageT", bound=Message)
ModelT = TypeVar("ModelT", bound=BaseModel)


class ProtobufMessageUtils:
    """
    Conversions between a protobuf message and the other shapes a contract takes.

    One schema produces two families of type: protobuf messages for gRPC, and
    pydantic models for HTTP. Proto3 canonical JSON is what both agree on —
    camelCase names, enums as their declared names, 64-bit integers as strings —
    so it carries a value between them without either being written down here.
    """

    @staticmethod
    def message_from_pydantic_model(model: BaseModel, message_type: type[MessageT]) -> MessageT:
        """
        Build a message of this type from a model of the same contract.

        Unset fields are dropped rather than sent as nulls, which proto3 JSON has
        no way to read.
        """
        message = message_type()
        ParseDict(model.model_dump(by_alias=True, exclude_none=True), message)
        return message

    @staticmethod
    def message_to_pydantic_model(message: Message, model_type: type[ModelT]) -> ModelT:
        """
        Build a model of this type from a message of the same contract.
        """
        return model_type.model_validate(MessageToDict(message))
