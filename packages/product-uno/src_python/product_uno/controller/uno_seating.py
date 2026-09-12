"""
How UNO seats its players.

Every open seat is offered as it is. A seat's number is its place in the turn
order, and it carries no role.
"""

from idl.lobby.model.seat_pb2 import SeatChoice, SeatStatus
from idl.lobby.model.table_pb2 import Table
from lobby.controller.base_seating import BaseSeating

from product_uno.adapters.uno_seat_adapters import UnoSeatAdapters


class UnoSeating(BaseSeating):
    """
    Every question the lobby asks a game about its seats, answered for UNO.
    """

    async def list_seat_choices(self, table: Table, player_id: str) -> tuple[SeatChoice, ...]:
        return tuple(
            UnoSeatAdapters.seat_number_to_seat_choice(seat.number)
            for seat in table.seats
            if seat.status == SeatStatus.SEAT_STATUS_OPEN
        )
