"""
How a piece is drawn.

Two figurine sets and two letter sets. The figurine sets are named for how they
look rather than for a colour, because which colour uses which is configurable —
see PieceGlyphs.glyph_for.
"""

from idl.chess.model.piece_pb2 import (
    COLOR_WHITE,
    PIECE_TYPE_BISHOP,
    PIECE_TYPE_KING,
    PIECE_TYPE_KNIGHT,
    PIECE_TYPE_PAWN,
    PIECE_TYPE_QUEEN,
    PIECE_TYPE_ROOK,
    Occupant,
    PieceType,
)

GlyphsByPieceType = dict[PieceType, str]

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

HOLLOW_UNICODE_GLYPHS_BY_PIECE_TYPE: GlyphsByPieceType = {
    PIECE_TYPE_KING: "♔",
    PIECE_TYPE_QUEEN: "♕",
    PIECE_TYPE_ROOK: "♖",
    PIECE_TYPE_BISHOP: "♗",
    PIECE_TYPE_KNIGHT: "♘",
    PIECE_TYPE_PAWN: "♙",
}

FILLED_UNICODE_GLYPHS_BY_PIECE_TYPE: GlyphsByPieceType = {
    PIECE_TYPE_KING: "♚",
    PIECE_TYPE_QUEEN: "♛",
    PIECE_TYPE_ROOK: "♜",
    PIECE_TYPE_BISHOP: "♝",
    PIECE_TYPE_KNIGHT: "♞",
    PIECE_TYPE_PAWN: "♟",
}

WHITE_ASCII_GLYPHS_BY_PIECE_TYPE: GlyphsByPieceType = {
    PIECE_TYPE_KING: "K",
    PIECE_TYPE_QUEEN: "Q",
    PIECE_TYPE_ROOK: "R",
    PIECE_TYPE_BISHOP: "B",
    PIECE_TYPE_KNIGHT: "N",
    PIECE_TYPE_PAWN: "P",
}

BLACK_ASCII_GLYPHS_BY_PIECE_TYPE: GlyphsByPieceType = {
    PIECE_TYPE_KING: "k",
    PIECE_TYPE_QUEEN: "q",
    PIECE_TYPE_ROOK: "r",
    PIECE_TYPE_BISHOP: "b",
    PIECE_TYPE_KNIGHT: "n",
    PIECE_TYPE_PAWN: "p",
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
                if occupant.color == COLOR_WHITE
                else BLACK_ASCII_GLYPHS_BY_PIECE_TYPE
            )
            return letters[occupant.piece_type]

        draw_hollow = (occupant.color == COLOR_WHITE) == transparent_white
        figurines = (
            HOLLOW_UNICODE_GLYPHS_BY_PIECE_TYPE
            if draw_hollow
            else FILLED_UNICODE_GLYPHS_BY_PIECE_TYPE
        )
        return figurines[occupant.piece_type]
