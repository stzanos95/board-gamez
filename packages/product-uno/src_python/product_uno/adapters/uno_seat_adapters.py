"""
A UNO seat, between the platform's shape and UNO's own.

A UNO seat carries no role, so nothing is packed or opened here: a seat is its
number, and a choice is a number.
"""

from core.protobuf.message_utils import ProtobufMessageUtils
from idl.lobby.model.seat_pb2 import Seat, SeatChoice, SeatChoiceCollection
from idl.lobby.model.seat_result_pb2 import SeatResult
from idl.lobby.model.table_pb2 import Table
from idl.uno.dto import table_pb2 as uno_table_dto_pb2
from idl.uno.model.table_pb2 import (
    UnoSeat,
    UnoSeatChoice,
    UnoSeatChoiceCollection,
    UnoSeatResult,
    UnoTable,
)
from idl_fastapi.idl.uno.dto import (
    ListSeatChoiceRequest,
    ListSeatChoiceResponse,
    ReadTableRequest,
    ReadTableResponse,
    TakeSeatRequest,
    TakeSeatResponse,
)


class UnoSeatAdapters:
    """
    Every UnoService seat message and every platform seat type, converted to
    what the layer beneath it takes.
    """

    # --- a request, to the arguments an operation takes ----------------------

    @staticmethod
    def read_table_request_to_table_id(request: uno_table_dto_pb2.ReadTableRequest) -> str:
        return request.table_id

    @staticmethod
    def list_request_to_table_id(request: uno_table_dto_pb2.ListSeatChoiceRequest) -> str:
        return request.table_id

    @staticmethod
    def list_request_to_player_id(request: uno_table_dto_pb2.ListSeatChoiceRequest) -> str:
        return request.player_id

    @staticmethod
    def take_request_to_table_id(request: uno_table_dto_pb2.TakeSeatRequest) -> str:
        return request.table_id

    @staticmethod
    def take_request_to_player_id(request: uno_table_dto_pb2.TakeSeatRequest) -> str:
        return request.player_id

    @staticmethod
    def take_request_to_choice(request: uno_table_dto_pb2.TakeSeatRequest) -> UnoSeatChoice:
        return request.choice

    @staticmethod
    def take_request_to_expected_version(request: uno_table_dto_pb2.TakeSeatRequest) -> int:
        return request.expected_version

    # --- what an operation answers, to a response ----------------------------

    @staticmethod
    def uno_table_to_read_response(
        table: UnoTable | None,
    ) -> uno_table_dto_pb2.ReadTableResponse:
        """
        An unset table is how the schema says no UNO table has that id.
        """
        return uno_table_dto_pb2.ReadTableResponse(table=table)

    @staticmethod
    def uno_seat_choice_collection_to_list_response(
        collection: UnoSeatChoiceCollection,
    ) -> uno_table_dto_pb2.ListSeatChoiceResponse:
        return uno_table_dto_pb2.ListSeatChoiceResponse(collection=collection)

    @staticmethod
    def uno_seat_result_to_take_response(
        result: UnoSeatResult,
    ) -> uno_table_dto_pb2.TakeSeatResponse:
        return uno_table_dto_pb2.TakeSeatResponse(result=result)

    # --- a pydantic model, to the message of the same contract ---------------

    @staticmethod
    def read_table_request_model_to_message(
        model: ReadTableRequest,
    ) -> uno_table_dto_pb2.ReadTableRequest:
        return ProtobufMessageUtils.message_from_pydantic_model(
            model, uno_table_dto_pb2.ReadTableRequest
        )

    @staticmethod
    def read_table_response_message_to_model(
        message: uno_table_dto_pb2.ReadTableResponse,
    ) -> ReadTableResponse:
        return ProtobufMessageUtils.message_to_pydantic_model(message, ReadTableResponse)

    @staticmethod
    def list_request_model_to_message(
        model: ListSeatChoiceRequest,
    ) -> uno_table_dto_pb2.ListSeatChoiceRequest:
        return ProtobufMessageUtils.message_from_pydantic_model(
            model, uno_table_dto_pb2.ListSeatChoiceRequest
        )

    @staticmethod
    def list_response_message_to_model(
        message: uno_table_dto_pb2.ListSeatChoiceResponse,
    ) -> ListSeatChoiceResponse:
        return ProtobufMessageUtils.message_to_pydantic_model(message, ListSeatChoiceResponse)

    @staticmethod
    def take_request_model_to_message(
        model: TakeSeatRequest,
    ) -> uno_table_dto_pb2.TakeSeatRequest:
        return ProtobufMessageUtils.message_from_pydantic_model(
            model, uno_table_dto_pb2.TakeSeatRequest
        )

    @staticmethod
    def take_response_message_to_model(
        message: uno_table_dto_pb2.TakeSeatResponse,
    ) -> TakeSeatResponse:
        return ProtobufMessageUtils.message_to_pydantic_model(message, TakeSeatResponse)

    # --- the platform's seats, to UNO's --------------------------------------

    @staticmethod
    def seat_number_to_seat_choice(number: int) -> SeatChoice:
        return SeatChoice(number=number)

    @staticmethod
    def uno_seat_choice_to_seat_choice(choice: UnoSeatChoice) -> SeatChoice:
        return SeatChoice(number=choice.number)

    @staticmethod
    def seat_choice_to_uno_seat_choice(choice: SeatChoice) -> UnoSeatChoice:
        return UnoSeatChoice(number=choice.number)

    @staticmethod
    def seat_choice_collection_to_uno_seat_choice_collection(
        collection: SeatChoiceCollection,
    ) -> UnoSeatChoiceCollection:
        return UnoSeatChoiceCollection(
            uno_seat_choice_items=tuple(
                UnoSeatAdapters.seat_choice_to_uno_seat_choice(choice)
                for choice in collection.seat_choice_items
            )
        )

    @staticmethod
    def seat_to_uno_seat(seat: Seat) -> UnoSeat:
        return UnoSeat(number=seat.number, status=seat.status, player_id=seat.player_id)

    @staticmethod
    def table_to_uno_table(table: Table) -> UnoTable:
        return UnoTable(
            id=table.id,
            status=table.status,
            seats=tuple(UnoSeatAdapters.seat_to_uno_seat(seat) for seat in table.seats),
            player_ids=table.player_ids,
            version=table.version,
        )

    @staticmethod
    def seat_result_to_uno_seat_result(result: SeatResult) -> UnoSeatResult:
        """
        The table is carried whatever the outcome, and stays unset when the
        lobby answered none.
        """
        table = (
            UnoSeatAdapters.table_to_uno_table(result.table) if result.HasField("table") else None
        )
        return UnoSeatResult(outcome=result.outcome, table=table)
