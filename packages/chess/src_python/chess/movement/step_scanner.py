"""
Single-step displacements, for pieces that leap rather than slide.

A leaper's reach does not depend on what stands between it and its target, so
each offset is one candidate square.
"""

from chess.contracts.board_state_view import BoardStateView
from chess.models.color import Color
from chess.models.move import Move
from chess.models.move_type import MoveType
from chess.models.piece_type import PieceType
from chess.models.square import Square
from chess.models.vector import Vector


class StepScanner:
    """
    Squares reachable by one fixed displacement, whatever lies between.
    """

    @staticmethod
    def moves_to_offsets(
        state: BoardStateView,
        origin: Square,
        color: Color,
        piece_type: PieceType,
        offsets: tuple[Vector, ...],
    ) -> tuple[Move, ...]:
        """
        Every move a leaper may make from this square, one per offset.

        An offset landing off the board or on an ally is skipped. There is no ray
        to stop, so one blocked offset says nothing about the others.
        """
        found: list[Move] = []
        for offset in offsets:
            square = origin.shifted(offset)
            if square is None or state.holds_ally_of(square, color):
                continue
            capturing = state.holds_enemy_of(square, color)
            found.append(
                Move(
                    origin=origin,
                    destination=square,
                    moving_color=color,
                    moving_piece_type=piece_type,
                    move_type=MoveType.CAPTURE if capturing else MoveType.QUIET,
                    captured_square=square if capturing else None,
                )
            )
        return tuple(found)

    @staticmethod
    def attacked_squares_at_offsets(
        origin: Square, offsets: tuple[Vector, ...]
    ) -> frozenset[Square]:
        """
        Every on-board square a leaper bears on from here.

        Takes no board at all: a leaper bears on each offset whoever stands
        there, and nothing between can block it.
        """
        landings = (origin.shifted(offset) for offset in offsets)
        return frozenset(square for square in landings if square is not None)
