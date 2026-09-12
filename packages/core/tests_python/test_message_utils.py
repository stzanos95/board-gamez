import unittest

from google.protobuf import any_pb2
from google.protobuf.descriptor_pb2 import FieldDescriptorProto
from google.protobuf.wrappers_pb2 import Int32Value, StringValue
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


class BinaryFormTest(unittest.TestCase):
    def test_a_message_survives_a_round_trip_through_its_bytes(self) -> None:
        message = FieldDescriptorProto(name="seats", number=FIELD_NUMBER)

        data = ProtobufMessageUtils.message_to_bytes(message)
        decoded = ProtobufMessageUtils.message_from_bytes(data, FieldDescriptorProto)

        self.assertEqual(decoded, message)

    def test_the_wire_form_is_bytes_and_not_text(self) -> None:
        data = ProtobufMessageUtils.message_to_bytes(FieldDescriptorProto(name="seats"))
        self.assertIsInstance(data, bytes)

    def test_an_empty_message_round_trips(self) -> None:
        data = ProtobufMessageUtils.message_to_bytes(FieldDescriptorProto())
        self.assertEqual(
            ProtobufMessageUtils.message_from_bytes(data, FieldDescriptorProto),
            FieldDescriptorProto(),
        )


class CopyingTest(unittest.TestCase):
    def test_a_copy_holds_the_same_values(self) -> None:
        message = FieldDescriptorProto(name="seats", number=FIELD_NUMBER)
        self.assertEqual(ProtobufMessageUtils.copy_of_message(message), message)

    def test_changing_a_copy_leaves_the_original_alone(self) -> None:
        message = FieldDescriptorProto(name="seats", number=FIELD_NUMBER)

        copied = ProtobufMessageUtils.copy_of_message(message)
        copied.name = "tables"

        self.assertEqual(message.name, "seats")
        self.assertEqual(copied.name, "tables")


class MessageFromAnyTest(unittest.TestCase):
    def test_a_message_of_the_packed_type_is_opened(self) -> None:
        packed = any_pb2.Any()
        packed.Pack(StringValue(value="hello"))
        opened = ProtobufMessageUtils.message_from_any(packed, StringValue)
        assert opened is not None
        self.assertEqual(opened.value, "hello")

    def test_a_message_of_another_type_is_not_opened(self) -> None:
        packed = any_pb2.Any()
        packed.Pack(StringValue(value="hello"))
        self.assertIsNone(ProtobufMessageUtils.message_from_any(packed, Int32Value))
