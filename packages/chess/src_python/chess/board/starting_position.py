"""
The position every game starts from.

Each call builds a new state. The back-rank order is the only fact worth stating;
the rest is symmetry between the two colours.
"""

from idl.chess.model.piece_pb2 import (
    COLOR_WHITE,
    PIECE_TYPE_BISHOP,
    PIECE_TYPE_KING,
    PIECE_TYPE_KNIGHT,
    PIECE_TYPE_PAWN,
    PIECE_TYPE_QUEEN,
    PIECE_TYPE_ROOK,
    Color,
    PieceType,
)
from idl.chess.model.square_pb2 import RANK_1, RANK_8, File, Rank, Square

from chess.board.chess_board_state import ChessBoardState
from chess.core.castling_rights import CastlingRightSets
from chess.core.colors import ALL_COLORS
from chess.core.files import ALL_FILES
from chess.pieces.base_piece import BasePiece
from chess.pieces.pawn_geometry import PawnGeometry
from chess.pieces.piece_factory import PieceFactory

STARTING_BACK_RANK_ORDER: tuple[PieceType, ...] = (
    PIECE_TYPE_ROOK,
    PIECE_TYPE_KNIGHT,
    PIECE_TYPE_BISHOP,
    PIECE_TYPE_QUEEN,
    PIECE_TYPE_KING,
    PIECE_TYPE_BISHOP,
    PIECE_TYPE_KNIGHT,
    PIECE_TYPE_ROOK,
)


class StartingPosition:
    """
    The opening position, built fresh on every call.
    """

    @staticmethod
    def build_state() -> ChessBoardState:
        """
        A new state with all thirty-two men home, White to move, all four
        castles available.
        """
        return ChessBoardState.from_pieces(
            pieces=(
                piece
                for color in ALL_COLORS
                for file in ALL_FILES
                for piece in (
                    StartingPosition._back_rank_piece(color=color, file=file),
                    StartingPosition._pawn(color=color, file=file),
                )
            ),
            side_to_move=COLOR_WHITE,
            castling_rights=CastlingRightSets.full(),
        )

    @staticmethod
    def _back_rank_of(color: Color) -> Rank:
        return RANK_1 if color == COLOR_WHITE else RANK_8

    @staticmethod
    def _back_rank_piece(color: Color, file: File) -> BasePiece:
        return PieceFactory.create_piece(
            piece_type=STARTING_BACK_RANK_ORDER[ALL_FILES.index(file)],
            color=color,
            square=Square(file=file, rank=StartingPosition._back_rank_of(color)),
        )

    @staticmethod
    def _pawn(color: Color, file: File) -> BasePiece:
        return PieceFactory.create_piece(
            piece_type=PIECE_TYPE_PAWN,
            color=color,
            square=Square(file=file, rank=PawnGeometry.start_rank(color)),
        )
