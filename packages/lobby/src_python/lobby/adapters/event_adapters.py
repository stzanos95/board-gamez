"""
A table, to the record of what was just done to it.

One method per write that succeeds. Each takes the table as stored after the
write, so the version an event carries is the version after it. A closed table
has no version after it.
"""

from idl.lobby.model.event_pb2 import (
    PlayerJoined,
    PlayerLeft,
    SeatTaken,
    SeatVacated,
    TableClosed,
    TableCreated,
)
from idl.lobby.model.seat_pb2 import SeatChoice
from idl.lobby.model.table_pb2 import Table

NO_SEAT_NUMBER = 0


class EventAdapters:
    """
    Every table event, built from the table it records.
    """

    @staticmethod
    def table_to_table_created(table: Table, player_id: str) -> TableCreated:
        return TableCreated(
            table_id=table.id,
            game_type=table.game_type,
            player_id=player_id,
            version=table.version,
        )

    @staticmethod
    def table_to_player_joined(table: Table, player_id: str) -> PlayerJoined:
        return PlayerJoined(table_id=table.id, player_id=player_id, version=table.version)

    @staticmethod
    def table_to_seat_taken(table: Table, player_id: str, choice: SeatChoice) -> SeatTaken:
        return SeatTaken(
            table_id=table.id,
            player_id=player_id,
            seat_number=choice.number,
            role=choice.role if choice.HasField("role") else None,
            version=table.version,
        )

    @staticmethod
    def table_to_seat_vacated(table: Table, player_id: str, seat_number: int) -> SeatVacated:
        return SeatVacated(
            table_id=table.id, player_id=player_id, seat_number=seat_number, version=table.version
        )

    @staticmethod
    def table_to_player_left(table: Table, player_id: str, seat_number: int) -> PlayerLeft:
        """
        `seat_number` is 0 when the player held no seat.
        """
        return PlayerLeft(
            table_id=table.id, player_id=player_id, seat_number=seat_number, version=table.version
        )

    @staticmethod
    def table_id_to_table_closed(table_id: str) -> TableClosed:
        return TableClosed(table_id=table_id)
