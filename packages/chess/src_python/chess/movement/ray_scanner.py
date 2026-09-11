"""
Walking a sliding piece's rays.

Bishop, rook and queen share this one implementation: travel until blocked, take
the first enemy square, stop short of an ally.
"""

from idl.chess.model.move_pb2 import MOVE_TYPE_CAPTURE, MOVE_TYPE_QUIET, Move
from idl.chess.model.piece_pb2 import Color, PieceType
from idl.chess.model.square_pb2 import Square

from chess.contracts.board_state_view import BoardStateView
from chess.core.squares import SquareIndex, Squares
from chess.movement.direction import Direction


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
            square = Squares.shifted(origin, direction.vector)
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
                        move_type=MOVE_TYPE_CAPTURE if capturing else MOVE_TYPE_QUIET,
                        captured_square=square if capturing else None,
                    )
                )
                if capturing:
                    break
                square = Squares.shifted(square, direction.vector)
        return tuple(found)

    @staticmethod
    def attacked_squares_along_rays(
        state: BoardStateView,
        origin: Square,
        directions: tuple[Direction, ...],
    ) -> frozenset[SquareIndex]:
        """
        Every square a slider bears on from here, in these directions.

        Differs from the move version in one way that matters: the blocking
        square is included whoever holds it. A piece defended by an ally is still
        defended, so the enemy king may not capture it.
        """
        found: set[SquareIndex] = set()
        for direction in directions:
            square = Squares.shifted(origin, direction.vector)
            while square is not None:
                found.add(Squares.get_index(square))
                if not state.is_empty(square):
                    break
                square = Squares.shifted(square, direction.vector)
        return frozenset(found)
