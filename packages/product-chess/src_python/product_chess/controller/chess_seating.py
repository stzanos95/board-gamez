"""
How chess seats its players.

The one place that decides which side a seat plays: the first seat is White and
the second is Black, and a seat is offered with the side its number fixes.
"""

from idl.lobby.model.seat_pb2 import SeatChoice, SeatStatus
from idl.lobby.model.table_pb2 import Table
from lobby.controller.base_seating import BaseSeating

from product_chess.adapters.chess_seat_adapters import ChessSeatAdapters


class ChessSeating(BaseSeating):
    """
    Every question the lobby asks a game about its seats, answered for chess.
    """

    async def list_seat_choices(self, table: Table, player_id: str) -> tuple[SeatChoice, ...]:
        return tuple(
            ChessSeatAdapters.seat_number_to_seat_choice(seat.number)
            for seat in table.seats
            if seat.status == SeatStatus.SEAT_STATUS_OPEN
        )
