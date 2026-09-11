"""
Building a piece from its type.

A new piece type is a class and a registry entry. Promotion and board setup
pick it up without change.
"""

from idl.chess.model.piece_pb2 import (
    PIECE_TYPE_BISHOP,
    PIECE_TYPE_KING,
    PIECE_TYPE_KNIGHT,
    PIECE_TYPE_PAWN,
    PIECE_TYPE_QUEEN,
    PIECE_TYPE_ROOK,
    Color,
    PieceType,
)
from idl.chess.model.square_pb2 import Square

from chess.pieces.base_piece import BasePiece
from chess.pieces.bishop import Bishop
from chess.pieces.king import King
from chess.pieces.knight import Knight
from chess.pieces.pawn import Pawn
from chess.pieces.queen import Queen
from chess.pieces.rook import Rook

PieceClassesByType = dict[PieceType, type[BasePiece]]

PIECE_CLASSES_BY_TYPE: PieceClassesByType = {
    PIECE_TYPE_PAWN: Pawn,
    PIECE_TYPE_KNIGHT: Knight,
    PIECE_TYPE_BISHOP: Bishop,
    PIECE_TYPE_ROOK: Rook,
    PIECE_TYPE_QUEEN: Queen,
    PIECE_TYPE_KING: King,
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
