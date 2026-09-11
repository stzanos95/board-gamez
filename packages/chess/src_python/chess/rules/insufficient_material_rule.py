"""
Draw because neither side has the material to deliver mate.

Recognises bare kings, king and one minor piece, and king and bishop against king
and bishop when both bishops travel on the same colour. Mate is impossible in
each against any defence.

Two knights against a lone king is excluded. Mate cannot be forced there but can
be reached against a cooperating defender, so the laws do not end the game.
"""

from idl.chess.model.piece_pb2 import (
    COLOR_BLACK,
    COLOR_WHITE,
    PIECE_TYPE_BISHOP,
    PIECE_TYPE_KING,
    PIECE_TYPE_PAWN,
    PIECE_TYPE_QUEEN,
    PIECE_TYPE_ROOK,
    Color,
    PieceType,
)
from idl.chess.model.square_pb2 import Square

from chess.board.chess_board_state import ChessBoardState
from chess.core.squares import Squares

MATING_PIECE_TYPES: tuple[PieceType, ...] = (PIECE_TYPE_PAWN, PIECE_TYPE_ROOK, PIECE_TYPE_QUEEN)
LONE_KINGS_MINOR_COUNT = 0
SINGLE_MINOR_COUNT = 1
BISHOP_PAIR_COUNT = 2


class InsufficientMaterialRule:
    """
    Draw because the material left on the board cannot mate.
    """

    @staticmethod
    def is_draw(state: ChessBoardState) -> bool:
        """
        Whether neither side has the material to force mate.

        Returns False the moment a pawn, rook or queen is seen, since any of
        those can mate on its own.
        """
        minor_squares_by_color: dict[Color, list[Square]] = {COLOR_WHITE: [], COLOR_BLACK: []}
        bishop_squares: list[Square] = []

        for piece in state.pieces.values():
            if piece.piece_type in MATING_PIECE_TYPES:
                return False
            if piece.piece_type == PIECE_TYPE_KING:
                continue
            minor_squares_by_color[piece.color].append(piece.square)
            if piece.piece_type == PIECE_TYPE_BISHOP:
                bishop_squares.append(piece.square)

        white_minors = len(minor_squares_by_color[COLOR_WHITE])
        black_minors = len(minor_squares_by_color[COLOR_BLACK])
        total_minors = white_minors + black_minors

        if total_minors == LONE_KINGS_MINOR_COUNT:
            return True
        if total_minors == SINGLE_MINOR_COUNT:
            return True
        if (
            total_minors == BISHOP_PAIR_COUNT
            and len(bishop_squares) == BISHOP_PAIR_COUNT
            and white_minors == SINGLE_MINOR_COUNT
            and black_minors == SINGLE_MINOR_COUNT
        ):
            # Bishops that never meet cannot combine to mate.
            return Squares.is_light(bishop_squares[0]) == Squares.is_light(bishop_squares[1])
        return False
