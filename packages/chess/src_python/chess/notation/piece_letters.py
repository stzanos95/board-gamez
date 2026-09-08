"""
The letters chess notation uses for the pieces.

A pawn is named by its file rather than by a letter, so its entry is the empty
string.
"""

from chess.models.piece_type import PieceType

NOTATION_LETTERS_BY_PIECE_TYPE: dict[PieceType, str] = {
    PieceType.PAWN: "",
    PieceType.KNIGHT: "N",
    PieceType.BISHOP: "B",
    PieceType.ROOK: "R",
    PieceType.QUEEN: "Q",
    PieceType.KING: "K",
}

PIECE_TYPES_BY_PROMOTION_LETTER: dict[str, PieceType] = {
    "q": PieceType.QUEEN,
    "r": PieceType.ROOK,
    "b": PieceType.BISHOP,
    "n": PieceType.KNIGHT,
}


class PieceLetters:
    """
    Translating between a piece type and the letter notation writes for it.
    """

    @staticmethod
    def notation_letter(piece_type: PieceType) -> str:
        """
        The upper-case letter a scoresheet uses, empty for a pawn.
        """
        return NOTATION_LETTERS_BY_PIECE_TYPE[piece_type]

    @staticmethod
    def promotion_letter(piece_type: PieceType) -> str:
        """
        The lower-case letter a coordinate move appends when promoting.
        """
        return NOTATION_LETTERS_BY_PIECE_TYPE[piece_type].lower()
