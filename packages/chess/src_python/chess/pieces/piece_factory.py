"""
Building a piece from its type.

A new piece type is a class and a registry entry. Promotion and board setup
pick it up without change.
"""

from chess.models.color import Color
from chess.models.piece_type import PieceType
from chess.models.square import Square
from chess.pieces.base_piece import BasePiece
from chess.pieces.bishop import Bishop
from chess.pieces.king import King
from chess.pieces.knight import Knight
from chess.pieces.pawn import Pawn
from chess.pieces.queen import Queen
from chess.pieces.rook import Rook

# Keys are data — a piece type names its class. This is a lookup, not a record.
PIECE_CLASSES_BY_TYPE: dict[PieceType, type[BasePiece]] = {
    PieceType.PAWN: Pawn,
    PieceType.KNIGHT: Knight,
    PieceType.BISHOP: Bishop,
    PieceType.ROOK: Rook,
    PieceType.QUEEN: Queen,
    PieceType.KING: King,
}


class PieceFactory:
    """
    The one place a piece is constructed from its type.
    """

    @staticmethod
    def create_piece(piece_type: PieceType, color: Color, square: Square) -> BasePiece:
        """
        A piece of this type, in this colour, standing on this square.
        """
        return PIECE_CLASSES_BY_TYPE[piece_type](color=color, square=square)
