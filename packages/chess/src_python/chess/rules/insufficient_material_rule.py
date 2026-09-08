"""
Draw because neither side has the material to deliver mate.

Recognises bare kings, king and one minor piece, and king and bishop against king
and bishop when both bishops travel on the same colour. Mate is impossible in
each against any defence.

Two knights against a lone king is excluded. Mate cannot be forced there but can
be reached against a cooperating defender, so the laws do not end the game.
"""

from chess.board.chess_board_state import ChessBoardState
from chess.models.color import Color
from chess.models.piece_type import PieceType
from chess.models.square import Square

MATING_PIECE_TYPES = (PieceType.PAWN, PieceType.ROOK, PieceType.QUEEN)
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
        minor_squares_by_color: dict[Color, list[Square]] = {Color.WHITE: [], Color.BLACK: []}
        bishop_squares: list[Square] = []

        for piece in state.pieces.values():
            if piece.piece_type in MATING_PIECE_TYPES:
                return False
            if piece.piece_type is PieceType.KING:
                continue
            minor_squares_by_color[piece.color].append(piece.square)
            if piece.piece_type is PieceType.BISHOP:
                bishop_squares.append(piece.square)

        white_minors = len(minor_squares_by_color[Color.WHITE])
        black_minors = len(minor_squares_by_color[Color.BLACK])
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
            return bishop_squares[0].is_light == bishop_squares[1].is_light
        return False
