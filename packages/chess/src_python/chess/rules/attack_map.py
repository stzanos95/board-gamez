"""
Which squares a side bears on.

A slider's reach stops at the first piece, including the enemy king, so a king
can appear able to step backwards along the line of a rook checking it. Legality
is decided by applying the move and asking again on the resulting position, where
that square is no longer blocked.
"""

from chess.board.chess_board_state import ChessBoardState
from chess.models.color import Color
from chess.models.square import Square


class AttackMap:
    """
    The squares a side attacks, gathered from every piece it has on the board.
    """

    @staticmethod
    def attacked_squares_for_color(state: ChessBoardState, color: Color) -> frozenset[Square]:
        """
        Every square this colour bears on.

        Includes squares held by its own pieces, since those are defended.
        """
        attacked: set[Square] = set()
        for piece in state.pieces_of(color):
            attacked |= piece.attacked_squares(state)
        return frozenset(attacked)

    @staticmethod
    def is_square_attacked_by(state: ChessBoardState, square: Square, color: Color) -> bool:
        """
        Whether this colour bears on one particular square.

        Stops at the first piece that does, so it is cheaper than building the
        whole map when only one square is in question.
        """
        return any(square in piece.attacked_squares(state) for piece in state.pieces_of(color))
