"""
How a piece is drawn.

Two figurine sets and two letter sets. The figurine sets are named for how they
look rather than for a colour, because which colour uses which is configurable —
see PieceGlyphs.glyph_for.
"""

from chess.models.color import Color
from chess.models.occupant import Occupant
from chess.models.piece_type import PieceType

# A full stop sits on the baseline, which reads as bottom-aligned beside the
# figurines. U+2219 BULLET OPERATOR sits at their height instead.
#
# It is also chosen for its width class. Every figurine is East Asian Width
# Neutral, so it occupies one column everywhere. U+00B7 MIDDLE DOT and U+2022
# BULLET are Ambiguous, which some terminals draw two columns wide — that
# makes empty ranks wider than occupied ones and the board stops lining up.
# Any replacement must be Neutral or Narrow; see the width test.
ASCII_EMPTY_SQUARE_GLYPH = "."
UNICODE_EMPTY_SQUARE_GLYPH = "∙"

HOLLOW_UNICODE_GLYPHS_BY_PIECE_TYPE: dict[PieceType, str] = {
    PieceType.KING: "♔",
    PieceType.QUEEN: "♕",
    PieceType.ROOK: "♖",
    PieceType.BISHOP: "♗",
    PieceType.KNIGHT: "♘",
    PieceType.PAWN: "♙",
}

FILLED_UNICODE_GLYPHS_BY_PIECE_TYPE: dict[PieceType, str] = {
    PieceType.KING: "♚",
    PieceType.QUEEN: "♛",
    PieceType.ROOK: "♜",
    PieceType.BISHOP: "♝",
    PieceType.KNIGHT: "♞",
    PieceType.PAWN: "♟",
}

WHITE_ASCII_GLYPHS_BY_PIECE_TYPE: dict[PieceType, str] = {
    PieceType.KING: "K",
    PieceType.QUEEN: "Q",
    PieceType.ROOK: "R",
    PieceType.BISHOP: "B",
    PieceType.KNIGHT: "N",
    PieceType.PAWN: "P",
}

BLACK_ASCII_GLYPHS_BY_PIECE_TYPE: dict[PieceType, str] = {
    PieceType.KING: "k",
    PieceType.QUEEN: "q",
    PieceType.ROOK: "r",
    PieceType.BISHOP: "b",
    PieceType.KNIGHT: "n",
    PieceType.PAWN: "p",
}


class PieceGlyphs:
    """
    Choosing the character that stands for a piece.
    """

    @staticmethod
    def empty_square_glyph(use_unicode: bool) -> str:
        """
        The character to draw for an empty square.

        Follows the same switch as the pieces, so a terminal that cannot draw
        figurines is not handed a middle dot either.
        """
        return UNICODE_EMPTY_SQUARE_GLYPH if use_unicode else ASCII_EMPTY_SQUARE_GLYPH

    @staticmethod
    def glyph_for(occupant: Occupant, use_unicode: bool, transparent_white: bool) -> str:
        """
        The character to draw for this occupant.

        `transparent_white` says which figurine set White gets. True gives White
        the hollow men, which is what Unicode intends and what looks right on a
        light background. False gives White the filled men, which is what looks
        right on a dark one, where the filled glyph is the bright one.

        Letters never swap: case already says which side owns the piece.
        """
        if not use_unicode:
            letters = (
                WHITE_ASCII_GLYPHS_BY_PIECE_TYPE
                if occupant.color is Color.WHITE
                else BLACK_ASCII_GLYPHS_BY_PIECE_TYPE
            )
            return letters[occupant.piece_type]

        draw_hollow = (occupant.color is Color.WHITE) == transparent_white
        figurines = (
            HOLLOW_UNICODE_GLYPHS_BY_PIECE_TYPE
            if draw_hollow
            else FILLED_UNICODE_GLYPHS_BY_PIECE_TYPE
        )
        return figurines[occupant.piece_type]
