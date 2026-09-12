"""
The controllers every hosted game shares.
"""

from dataclasses import dataclass

from game.controller.game_spec_controller import GameSpecController
from game.controller.session_controller import SessionController
from lobby.controller.seat_controller import SeatController
from lobby.controller.table_controller import TableController


@dataclass(frozen=True, slots=True)
class PlatformControllers:
    """
    The platform's controllers, built once from the configuration.

    Every one that writes publishes through the one publisher. A product
    composes these; it never builds its own.
    """

    tables: TableController
    seats: SeatController
    sessions: SessionController
    game_specs: GameSpecController
