"""
A seat, between the shapes it takes.

A choice is a seat number and a role; taking it produces a table with that seat
occupied, and giving it up produces one with that seat open. Opening a table
produces one with every seat open, joining one produces one with one more
player at it, and starting the game produces one in progress. Building those
tables is a conversion and runs here, so the controller that decides whether a
change may be made never assembles one.

A contract also produces two families of type — protobuf messages for gRPC and
pydantic models for HTTP — and a caller crossing between them converts here too.
"""

from core.protobuf.message_utils import ProtobufMessageUtils
from idl.game.model.game_type_pb2 import GameType
from idl.lobby.dto import seat_pb2
from idl.lobby.model.seat_pb2 import Seat, SeatChoice, SeatChoiceCollection, SeatStatus
from idl.lobby.model.seat_result_pb2 import SeatResult
from idl.lobby.model.table_pb2 import Table, TableStatus
from idl_fastapi.idl.lobby.dto import (
    CreateTableRequest,
    CreateTableResponse,
    JoinTableRequest,
    JoinTableResponse,
    LeaveTableRequest,
    LeaveTableResponse,
    VacateSeatRequest,
    VacateSeatResponse,
)

FIRST_SEAT_NUMBER = 1
NEVER_STORED_VERSION = 0


class SeatAdapters:
    """
    Every seat shape, converted to the one the layer beneath it takes.
    """

    # --- a request, to the arguments an operation takes ----------------------

    @staticmethod
    def create_request_to_game_type(request: seat_pb2.CreateTableRequest) -> GameType:
        return request.game_type

    @staticmethod
    def create_request_to_seat_count(request: seat_pb2.CreateTableRequest) -> int:
        return request.seat_count

    @staticmethod
    def create_request_to_player_id(request: seat_pb2.CreateTableRequest) -> str:
        return request.player_id

    @staticmethod
    def join_request_to_table_id(request: seat_pb2.JoinTableRequest) -> str:
        return request.table_id

    @staticmethod
    def join_request_to_player_id(request: seat_pb2.JoinTableRequest) -> str:
        return request.player_id

    @staticmethod
    def vacate_request_to_table_id(request: seat_pb2.VacateSeatRequest) -> str:
        return request.table_id

    @staticmethod
    def vacate_request_to_player_id(request: seat_pb2.VacateSeatRequest) -> str:
        return request.player_id

    @staticmethod
    def leave_request_to_table_id(request: seat_pb2.LeaveTableRequest) -> str:
        return request.table_id

    @staticmethod
    def leave_request_to_player_id(request: seat_pb2.LeaveTableRequest) -> str:
        return request.player_id

    # --- what an operation answers, to a response ----------------------------

    @staticmethod
    def seat_result_to_create_response(result: SeatResult) -> seat_pb2.CreateTableResponse:
        return seat_pb2.CreateTableResponse(result=result)

    @staticmethod
    def seat_result_to_join_response(result: SeatResult) -> seat_pb2.JoinTableResponse:
        return seat_pb2.JoinTableResponse(result=result)

    @staticmethod
    def seat_result_to_vacate_response(result: SeatResult) -> seat_pb2.VacateSeatResponse:
        return seat_pb2.VacateSeatResponse(result=result)

    @staticmethod
    def seat_result_to_leave_response(result: SeatResult) -> seat_pb2.LeaveTableResponse:
        return seat_pb2.LeaveTableResponse(result=result)

    # --- a pydantic model, to the message of the same contract ---------------

    @staticmethod
    def create_request_model_to_message(model: CreateTableRequest) -> seat_pb2.CreateTableRequest:
        return ProtobufMessageUtils.message_from_pydantic_model(model, seat_pb2.CreateTableRequest)

    @staticmethod
    def create_response_message_to_model(
        message: seat_pb2.CreateTableResponse,
    ) -> CreateTableResponse:
        return ProtobufMessageUtils.message_to_pydantic_model(message, CreateTableResponse)

    @staticmethod
    def join_request_model_to_message(model: JoinTableRequest) -> seat_pb2.JoinTableRequest:
        return ProtobufMessageUtils.message_from_pydantic_model(model, seat_pb2.JoinTableRequest)

    @staticmethod
    def join_response_message_to_model(
        message: seat_pb2.JoinTableResponse,
    ) -> JoinTableResponse:
        return ProtobufMessageUtils.message_to_pydantic_model(message, JoinTableResponse)

    @staticmethod
    def vacate_request_model_to_message(model: VacateSeatRequest) -> seat_pb2.VacateSeatRequest:
        return ProtobufMessageUtils.message_from_pydantic_model(model, seat_pb2.VacateSeatRequest)

    @staticmethod
    def vacate_response_message_to_model(
        message: seat_pb2.VacateSeatResponse,
    ) -> VacateSeatResponse:
        return ProtobufMessageUtils.message_to_pydantic_model(message, VacateSeatResponse)

    @staticmethod
    def leave_request_model_to_message(model: LeaveTableRequest) -> seat_pb2.LeaveTableRequest:
        return ProtobufMessageUtils.message_from_pydantic_model(model, seat_pb2.LeaveTableRequest)

    @staticmethod
    def leave_response_message_to_model(
        message: seat_pb2.LeaveTableResponse,
    ) -> LeaveTableResponse:
        return ProtobufMessageUtils.message_to_pydantic_model(message, LeaveTableResponse)

    # --- a table, to the table after a change ---------------------------------

    @staticmethod
    def seat_choices_to_collection(choices: tuple[SeatChoice, ...]) -> SeatChoiceCollection:
        return SeatChoiceCollection(seat_choice_items=choices)

    @staticmethod
    def creation_to_table(
        table_id: str, game_type: GameType, seat_count: int, player_id: str
    ) -> Table:
        """
        A table nobody has stored yet, waiting for players, with the opener at
        it and every seat open. Version 0 is what tells the store this is a
        creation.
        """
        return Table(
            id=table_id,
            game_type=game_type,
            status=TableStatus.TABLE_STATUS_WAITING,
            seats=SeatAdapters.seat_count_to_open_seats(seat_count),
            version=NEVER_STORED_VERSION,
            player_ids=(player_id,),
        )

    @staticmethod
    def seat_count_to_open_seats(seat_count: int) -> tuple[Seat, ...]:
        """
        This many open seats, numbered from 1.
        """
        return tuple(
            Seat(number=FIRST_SEAT_NUMBER + index, status=SeatStatus.SEAT_STATUS_OPEN)
            for index in range(seat_count)
        )

    @staticmethod
    def table_to_table_with_player_joined(table: Table, player_id: str) -> Table:
        """
        The table with this player at it, seated nowhere. The table handed in
        is not changed.
        """
        return Table(
            id=table.id,
            game_type=table.game_type,
            status=table.status,
            seats=table.seats,
            version=table.version,
            player_ids=(*table.player_ids, player_id),
        )

    @staticmethod
    def table_to_table_finished(table: Table) -> Table:
        """
        The table with its game over. The table handed in is not changed.
        """
        return Table(
            id=table.id,
            game_type=table.game_type,
            status=TableStatus.TABLE_STATUS_FINISHED,
            seats=table.seats,
            version=table.version,
            player_ids=table.player_ids,
        )

    @staticmethod
    def table_to_table_in_progress(table: Table) -> Table:
        """
        The table with its game being played. The table handed in is not
        changed.
        """
        return Table(
            id=table.id,
            game_type=table.game_type,
            status=TableStatus.TABLE_STATUS_IN_PROGRESS,
            seats=table.seats,
            version=table.version,
            player_ids=table.player_ids,
        )

    @staticmethod
    def table_to_table_with_seat_vacated(table: Table, player_id: str) -> Table:
        """
        The table with this player's seat open and the player still at the
        table. The table handed in is not changed.
        """
        return Table(
            id=table.id,
            game_type=table.game_type,
            status=table.status,
            seats=SeatAdapters._seats_without(table, player_id),
            version=table.version,
            player_ids=table.player_ids,
        )

    @staticmethod
    def table_to_table_with_player_left(table: Table, player_id: str) -> Table:
        """
        The table with this player gone from every seat and from the table. The
        table handed in is not changed.
        """
        return Table(
            id=table.id,
            game_type=table.game_type,
            status=table.status,
            seats=SeatAdapters._seats_without(table, player_id),
            version=table.version,
            player_ids=tuple(at_table for at_table in table.player_ids if at_table != player_id),
        )

    @staticmethod
    def _seats_without(table: Table, player_id: str) -> tuple[Seat, ...]:
        return tuple(
            SeatAdapters._seat_vacated(seat) if seat.player_id == player_id else seat
            for seat in table.seats
        )

    @staticmethod
    def _seat_vacated(seat: Seat) -> Seat:
        return Seat(number=seat.number, status=SeatStatus.SEAT_STATUS_OPEN)

    @staticmethod
    def table_to_table_with_seat_taken(table: Table, player_id: str, choice: SeatChoice) -> Table:
        """
        The table with the chosen seat occupied by this player, and the player
        at the table. The table handed in is not changed.
        """
        return Table(
            id=table.id,
            game_type=table.game_type,
            status=table.status,
            seats=tuple(
                SeatAdapters._seat_occupied_by(seat, player_id, choice)
                if seat.number == choice.number
                else seat
                for seat in table.seats
            ),
            version=table.version,
            player_ids=(
                table.player_ids
                if player_id in table.player_ids
                else (*table.player_ids, player_id)
            ),
        )

    @staticmethod
    def _seat_occupied_by(seat: Seat, player_id: str, choice: SeatChoice) -> Seat:
        return Seat(
            number=seat.number,
            status=SeatStatus.SEAT_STATUS_OCCUPIED,
            player_id=player_id,
            role=choice.role if choice.HasField("role") else None,
        )
