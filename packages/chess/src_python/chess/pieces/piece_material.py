"""
Conventional material values.

Used by the insufficient-material rule and for display. Nothing in this engine
searches or evaluates.
"""

from chess.models.piece_type import PieceType

PAWN_MATERIAL_VALUE = 1
KNIGHT_MATERIAL_VALUE = 3
BISHOP_MATERIAL_VALUE = 3
ROOK_MATERIAL_VALUE = 5
QUEEN_MATERIAL_VALUE = 9
KING_MATERIAL_VALUE = 0

MATERIAL_VALUES_BY_PIECE_TYPE: dict[PieceType, int] = {
    PieceType.PAWN: PAWN_MATERIAL_VALUE,
    PieceType.KNIGHT: KNIGHT_MATERIAL_VALUE,
    PieceType.BISHOP: BISHOP_MATERIAL_VALUE,
    PieceType.ROOK: ROOK_MATERIAL_VALUE,
    PieceType.QUEEN: QUEEN_MATERIAL_VALUE,
    PieceType.KING: KING_MATERIAL_VALUE,
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
