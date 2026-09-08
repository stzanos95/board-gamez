"""
The position every game starts from.

Each call builds a new state. The back-rank order is the only fact worth stating;
the rest is symmetry between the two colours.
"""

from chess.board.chess_board_state import ChessBoardState
from chess.models.castling_rights import CastlingRights
from chess.models.color import Color
from chess.models.file_index import File
from chess.models.piece_type import PieceType
from chess.models.rank_index import Rank
from chess.models.square import Square
from chess.pieces.base_piece import BasePiece
from chess.pieces.pawn_geometry import PawnGeometry
from chess.pieces.piece_factory import PieceFactory

STARTING_BACK_RANK_ORDER: tuple[PieceType, ...] = (
    PieceType.ROOK,
    PieceType.KNIGHT,
    PieceType.BISHOP,
    PieceType.QUEEN,
    PieceType.KING,
    PieceType.BISHOP,
    PieceType.KNIGHT,
    PieceType.ROOK,
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
                for color in Color
                for file in File
                for piece in (
                    StartingPosition._back_rank_piece(color=color, file=file),
                    StartingPosition._pawn(color=color, file=file),
                )
            ),
            side_to_move=Color.WHITE,
            castling_rights=CastlingRights.full(),
        )

    @staticmethod
    def _back_rank_of(color: Color) -> Rank:
        return Rank.ONE if color is Color.WHITE else Rank.EIGHT

    @staticmethod
    def _back_rank_piece(color: Color, file: File) -> BasePiece:
        return PieceFactory.create_piece(
            piece_type=STARTING_BACK_RANK_ORDER[file.value],
            color=color,
            square=Square(file=file, rank=StartingPosition._back_rank_of(color)),
        )

    @staticmethod
    def _pawn(color: Color, file: File) -> BasePiece:
        return PieceFactory.create_piece(
            piece_type=PieceType.PAWN,
            color=color,
            square=Square(file=file, rank=PawnGeometry.start_rank(color)),
        )
