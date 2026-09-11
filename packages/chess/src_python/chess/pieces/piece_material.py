"""
Conventional material values.

Used by the insufficient-material rule and for display. Nothing in this engine
searches or evaluates.
"""

from idl.chess.model.piece_pb2 import (
    PIECE_TYPE_BISHOP,
    PIECE_TYPE_KING,
    PIECE_TYPE_KNIGHT,
    PIECE_TYPE_PAWN,
    PIECE_TYPE_QUEEN,
    PIECE_TYPE_ROOK,
    PieceType,
)

PAWN_MATERIAL_VALUE = 1
KNIGHT_MATERIAL_VALUE = 3
BISHOP_MATERIAL_VALUE = 3
ROOK_MATERIAL_VALUE = 5
QUEEN_MATERIAL_VALUE = 9
KING_MATERIAL_VALUE = 0

MaterialValuesByPieceType = dict[PieceType, int]

MATERIAL_VALUES_BY_PIECE_TYPE: MaterialValuesByPieceType = {
    PIECE_TYPE_PAWN: PAWN_MATERIAL_VALUE,
    PIECE_TYPE_KNIGHT: KNIGHT_MATERIAL_VALUE,
    PIECE_TYPE_BISHOP: BISHOP_MATERIAL_VALUE,
    PIECE_TYPE_ROOK: ROOK_MATERIAL_VALUE,
    PIECE_TYPE_QUEEN: QUEEN_MATERIAL_VALUE,
    PIECE_TYPE_KING: KING_MATERIAL_VALUE,
}


class PieceMaterial:
    """
    What each piece is conventionally worth.
    """

    @staticmethod
    def value_of(piece_type: PieceType) -> int:
        """
        The conventional value of one piece of this type. A king scores zero
        because it is never traded.
        """
        return MATERIAL_VALUES_BY_PIECE_TYPE[piece_type]
