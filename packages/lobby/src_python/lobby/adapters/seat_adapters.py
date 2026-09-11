"""
A seat, between the shapes it takes.

A choice is a seat number and a role; taking it produces a table with that seat
occupied. Building that table is a conversion and runs here, so the controller
that decides whether the seat may be taken never assembles one.
"""

from idl.lobby.model.seat_pb2 import Seat, SeatChoice, SeatChoiceCollection, SeatStatus
from idl.lobby.model.table_pb2 import Table


class SeatAdapters:
    """
    Every seat shape, converted to the one the layer beneath it takes.
    """

    @staticmethod
    def seat_choices_to_collection(choices: tuple[SeatChoice, ...]) -> SeatChoiceCollection:
        return SeatChoiceCollection(seat_choice_items=choices)

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
