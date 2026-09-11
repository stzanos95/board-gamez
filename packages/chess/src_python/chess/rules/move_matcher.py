"""
Turning a move as a player names it into a move the board can apply.
"""

from idl.chess.model.move_pb2 import CoordinateMove, Move
from idl.chess.model.square_pb2 import FILE_UNSPECIFIED, RANK_UNSPECIFIED, Square


class MoveMatcher:
    """
    Matching a coordinate move against the legal moves of a position.
    """

    @staticmethod
    def get_legal_move(
        coordinate_move: CoordinateMove, legal_moves: tuple[Move, ...]
    ) -> Move | None:
        """
        The legal move the coordinate move names, or None if there is no such
        move.

        A promotion is matched only when the coordinate move says what the pawn
        becomes; without that, no move matches.
        """
        if not MoveMatcher._is_named(coordinate_move.origin) or not MoveMatcher._is_named(
            coordinate_move.destination
        ):
            return None
        for move in legal_moves:
            if (
                move.origin == coordinate_move.origin
                and move.destination == coordinate_move.destination
                and move.promotion_type == coordinate_move.promotion_type
            ):
                return move
        return None

    @staticmethod
    def _is_named(square: Square) -> bool:
        return square.file != FILE_UNSPECIFIED and square.rank != RANK_UNSPECIFIED
