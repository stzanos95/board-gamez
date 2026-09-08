from enum import Enum


class PieceType(Enum):
    """
    The six types of chessman.
    """

    PAWN = "pawn"
    KNIGHT = "knight"
    BISHOP = "bishop"
    ROOK = "rook"
    QUEEN = "queen"
    KING = "king"
