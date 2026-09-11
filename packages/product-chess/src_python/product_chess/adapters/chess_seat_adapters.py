"""
A chess seat, between the platform's shape and chess's own.

The platform carries a seat's role opaquely. Packing a side into one and opening
one back into a side runs here and nowhere else, so no layer above this file
reads a role.
"""

from core.protobuf.message_utils import ProtobufMessageUtils
from google.protobuf import any_pb2
from idl.chess.dto import table_pb2 as chess_table_dto_pb2
from idl.chess.model.piece_pb2 import COLOR_BLACK, COLOR_UNSPECIFIED, COLOR_WHITE, Color
from idl.chess.model.side_pb2 import ChessSide
from idl.chess.model.table_pb2 import (
    ChessSeat,
    ChessSeatChoice,
    ChessSeatChoiceCollection,
    ChessSeatResult,
    ChessTable,
)
from idl.lobby.model.seat_pb2 import Seat, SeatChoice, SeatChoiceCollection
from idl.lobby.model.seat_result_pb2 import SeatResult
from idl.lobby.model.table_pb2 import Table
from idl_fastapi.idl.chess.dto import (
    ListSeatChoiceRequest,
    ListSeatChoiceResponse,
    ReadTableRequest,
    ReadTableResponse,
    TakeSeatRequest,
    TakeSeatResponse,
)

WHITE_SEAT_NUMBER = 1
BLACK_SEAT_NUMBER = 2

COLORS_BY_SEAT_NUMBER: dict[int, Color] = {
    WHITE_SEAT_NUMBER: COLOR_WHITE,
    BLACK_SEAT_NUMBER: COLOR_BLACK,
}


class ChessSeatAdapters:
    """
    Every ChessService seat message and every platform seat type, converted to
    what the layer beneath it takes.
    """

    # --- a request, to the arguments an operation takes ----------------------

    @staticmethod
    def read_table_request_to_table_id(request: chess_table_dto_pb2.ReadTableRequest) -> str:
        return request.table_id

    @staticmethod
    def list_request_to_table_id(request: chess_table_dto_pb2.ListSeatChoiceRequest) -> str:
        return request.table_id

    @staticmethod
    def list_request_to_player_id(request: chess_table_dto_pb2.ListSeatChoiceRequest) -> str:
        return request.player_id

    @staticmethod
    def take_request_to_table_id(request: chess_table_dto_pb2.TakeSeatRequest) -> str:
        return request.table_id

    @staticmethod
    def take_request_to_player_id(request: chess_table_dto_pb2.TakeSeatRequest) -> str:
        return request.player_id

    @staticmethod
    def take_request_to_choice(request: chess_table_dto_pb2.TakeSeatRequest) -> ChessSeatChoice:
        return request.choice

    @staticmethod
    def take_request_to_expected_version(request: chess_table_dto_pb2.TakeSeatRequest) -> int:
        return request.expected_version

    # --- what an operation answers, to a response ----------------------------

    @staticmethod
    def chess_table_to_read_response(
        table: ChessTable | None,
    ) -> chess_table_dto_pb2.ReadTableResponse:
        """
        An unset table is how the schema says no chess table has that id.
        """
        return chess_table_dto_pb2.ReadTableResponse(table=table)

    @staticmethod
    def chess_seat_choice_collection_to_list_response(
        collection: ChessSeatChoiceCollection,
    ) -> chess_table_dto_pb2.ListSeatChoiceResponse:
        return chess_table_dto_pb2.ListSeatChoiceResponse(collection=collection)

    @staticmethod
    def chess_seat_result_to_take_response(
        result: ChessSeatResult,
    ) -> chess_table_dto_pb2.TakeSeatResponse:
        return chess_table_dto_pb2.TakeSeatResponse(result=result)

    # --- a pydantic model, to the message of the same contract ---------------

    @staticmethod
    def read_table_request_model_to_message(
        model: ReadTableRequest,
    ) -> chess_table_dto_pb2.ReadTableRequest:
        return ProtobufMessageUtils.message_from_pydantic_model(
            model, chess_table_dto_pb2.ReadTableRequest
        )

    @staticmethod
    def read_table_response_message_to_model(
        message: chess_table_dto_pb2.ReadTableResponse,
    ) -> ReadTableResponse:
        return ProtobufMessageUtils.message_to_pydantic_model(message, ReadTableResponse)

    @staticmethod
    def list_request_model_to_message(
        model: ListSeatChoiceRequest,
    ) -> chess_table_dto_pb2.ListSeatChoiceRequest:
        return ProtobufMessageUtils.message_from_pydantic_model(
            model, chess_table_dto_pb2.ListSeatChoiceRequest
        )

    @staticmethod
    def list_response_message_to_model(
        message: chess_table_dto_pb2.ListSeatChoiceResponse,
    ) -> ListSeatChoiceResponse:
        return ProtobufMessageUtils.message_to_pydantic_model(message, ListSeatChoiceResponse)

    @staticmethod
    def take_request_model_to_message(
        model: TakeSeatRequest,
    ) -> chess_table_dto_pb2.TakeSeatRequest:
        return ProtobufMessageUtils.message_from_pydantic_model(
            model, chess_table_dto_pb2.TakeSeatRequest
        )

    @staticmethod
    def take_response_message_to_model(
        message: chess_table_dto_pb2.TakeSeatResponse,
    ) -> TakeSeatResponse:
        return ProtobufMessageUtils.message_to_pydantic_model(message, TakeSeatResponse)

    # --- a side, to the role the platform carries, and back -----------------

    @staticmethod
    def color_to_role(color: Color) -> any_pb2.Any:
        role = any_pb2.Any()
        role.Pack(ChessSide(color=color))
        return role

    @staticmethod
    def role_to_color(role: any_pb2.Any) -> Color:
        """
        The side a role names, or unset when the role is not a chess side.
        """
        side = ChessSide()
        if not role.Unpack(side):
            return COLOR_UNSPECIFIED
        return side.color

    @staticmethod
    def seat_number_to_color(number: int) -> Color:
        """
        The side a seat plays, fixed by its number; unset for a seat chess has
        no side for.
        """
        return COLORS_BY_SEAT_NUMBER.get(number, COLOR_UNSPECIFIED)

    # --- the platform's seats, to chess's ----------------------------------

    @staticmethod
    def seat_number_to_seat_choice(number: int) -> SeatChoice:
        return SeatChoice(
            number=number,
            role=ChessSeatAdapters.color_to_role(ChessSeatAdapters.seat_number_to_color(number)),
        )

    @staticmethod
    def chess_seat_choice_to_seat_choice(choice: ChessSeatChoice) -> SeatChoice:
        return SeatChoice(number=choice.number, role=ChessSeatAdapters.color_to_role(choice.color))

    @staticmethod
    def seat_choice_to_chess_seat_choice(choice: SeatChoice) -> ChessSeatChoice:
        return ChessSeatChoice(
            number=choice.number, color=ChessSeatAdapters.role_to_color(choice.role)
        )

    @staticmethod
    def seat_choice_collection_to_chess_seat_choice_collection(
        collection: SeatChoiceCollection,
    ) -> ChessSeatChoiceCollection:
        return ChessSeatChoiceCollection(
            chess_seat_choice_items=tuple(
                ChessSeatAdapters.seat_choice_to_chess_seat_choice(choice)
                for choice in collection.seat_choice_items
            )
        )

    @staticmethod
    def seat_to_chess_seat(seat: Seat) -> ChessSeat:
        return ChessSeat(
            number=seat.number,
            status=seat.status,
            player_id=seat.player_id,
            color=ChessSeatAdapters.role_to_color(seat.role),
        )

    @staticmethod
    def table_to_chess_table(table: Table) -> ChessTable:
        return ChessTable(
            id=table.id,
            status=table.status,
            seats=tuple(ChessSeatAdapters.seat_to_chess_seat(seat) for seat in table.seats),
            player_ids=table.player_ids,
            version=table.version,
        )

    @staticmethod
    def seat_result_to_chess_seat_result(result: SeatResult) -> ChessSeatResult:
        """
        The table is carried whatever the outcome, and stays unset when the
        lobby answered none.
        """
        table = (
            ChessSeatAdapters.table_to_chess_table(result.table)
            if result.HasField("table")
            else None
        )
        return ChessSeatResult(outcome=result.outcome, table=table)
