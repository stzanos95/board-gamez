"""
The letters chess notation uses for the pieces.

A pawn is named by its file rather than by a letter, so its entry is the empty
string.
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

NotationLettersByPieceType = dict[PieceType, str]
PieceTypesByPromotionLetter = dict[str, PieceType]

NOTATION_LETTERS_BY_PIECE_TYPE: NotationLettersByPieceType = {
    PIECE_TYPE_PAWN: "",
    PIECE_TYPE_KNIGHT: "N",
    PIECE_TYPE_BISHOP: "B",
    PIECE_TYPE_ROOK: "R",
    PIECE_TYPE_QUEEN: "Q",
    PIECE_TYPE_KING: "K",
}

PIECE_TYPES_BY_PROMOTION_LETTER: PieceTypesByPromotionLetter = {
    "q": PIECE_TYPE_QUEEN,
    "r": PIECE_TYPE_ROOK,
    "b": PIECE_TYPE_BISHOP,
    "n": PIECE_TYPE_KNIGHT,
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
