"""
Walking a sliding piece's rays.

Bishop, rook and queen share this one implementation: travel until blocked, take
the first enemy square, stop short of an ally.
"""

from chess.contracts.board_state_view import BoardStateView
from chess.models.color import Color
from chess.models.direction import Direction
from chess.models.move import Move
from chess.models.move_type import MoveType
from chess.models.piece_type import PieceType
from chess.models.square import Square


class RayScanner:
    """
    Squares reachable by travelling in a straight line until something stops you.
    """

    @staticmethod
    def moves_along_rays(
        state: BoardStateView,
        origin: Square,
        color: Color,
        piece_type: PieceType,
        directions: tuple[Direction, ...],
    ) -> tuple[Move, ...]:
        """
        Every move a slider may make from this square, in these directions.

        Each ray runs until it leaves the board or meets a piece. An enemy square
        is included and ends the ray, because a slider may capture but not pass
        through. An ally square ends the ray without being included.
        """
        found: list[Move] = []
        for direction in directions:
            square = origin.shifted(direction.vector)
            while square is not None:
                if state.holds_ally_of(square, color):
                    break
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
                if capturing:
                    break
                square = square.shifted(direction.vector)
        return tuple(found)

    @staticmethod
    def attacked_squares_along_rays(
        state: BoardStateView,
        origin: Square,
        directions: tuple[Direction, ...],
    ) -> frozenset[Square]:
        """
        Every square a slider bears on from here, in these directions.

        Differs from the move version in one way that matters: the blocking
        square is included whoever holds it. A piece defended by an ally is still
        defended, so the enemy king may not capture it.
        """
        found: set[Square] = set()
        for direction in directions:
            square = origin.shifted(direction.vector)
            while square is not None:
                found.add(square)
                if not state.is_empty(square):
                    break
                square = square.shifted(direction.vector)
        return frozenset(found)
