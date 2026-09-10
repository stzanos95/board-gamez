import unittest

from google.protobuf.descriptor_pb2 import FieldDescriptorProto
from pydantic import BaseModel, ConfigDict, Field

from core.protobuf.message_utils import ProtobufMessageUtils

FIELD_NUMBER = 7


# pydantic's BaseModel declares Any in its own signature, which the house ban on
# explicit Any catches at every subclass. The rule is about what is written here.
class FieldModel(BaseModel):  # type: ignore[explicit-any]
    """
    A model of a message this package does not own, so the conversion is tested
    without a schema of its own to depend on.
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str | None = None
    number: int | None = None
    type_name: str | None = Field(default=None, alias="typeName")


class ConvertingTest(unittest.TestCase):
    def test_a_model_becomes_the_message_it_describes(self) -> None:
        message = ProtobufMessageUtils.message_from_pydantic_model(
            FieldModel(name="seats", number=FIELD_NUMBER), FieldDescriptorProto
        )
        self.assertEqual(message.name, "seats")
        self.assertEqual(message.number, FIELD_NUMBER)

    def test_a_message_becomes_the_model_it_describes(self) -> None:
        message = FieldDescriptorProto(name="seats", number=FIELD_NUMBER)
        model = ProtobufMessageUtils.message_to_pydantic_model(message, FieldModel)
        self.assertEqual(model.name, "seats")
        self.assertEqual(model.number, FIELD_NUMBER)

    def test_a_field_the_model_left_unset_is_not_sent(self) -> None:
        message = ProtobufMessageUtils.message_from_pydantic_model(
            FieldModel(name="seats"), FieldDescriptorProto
        )
        self.assertFalse(message.HasField("number"))

    def test_a_camel_cased_name_survives_the_round_trip(self) -> None:
        original = FieldModel.model_validate({"name": "seats", "typeName": ".idl.lobby.model.Seat"})
        message = ProtobufMessageUtils.message_from_pydantic_model(original, FieldDescriptorProto)
        self.assertEqual(message.type_name, ".idl.lobby.model.Seat")
        self.assertEqual(
            ProtobufMessageUtils.message_to_pydantic_model(message, FieldModel).type_name,
            ".idl.lobby.model.Seat",
        )
