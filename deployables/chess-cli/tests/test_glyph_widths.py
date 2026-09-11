"""
Every glyph the board can draw must occupy exactly one terminal column.
"""

import unicodedata
import unittest

from chess.core.colors import ALL_COLORS
from idl.chess.model.piece_pb2 import Occupant

from chess_cli.display.piece_glyphs import HOLLOW_UNICODE_GLYPHS_BY_PIECE_TYPE, PieceGlyphs

# Narrow and Neutral are one column everywhere. Ambiguous is one column on some
# terminals and two on others, which silently misaligns the board; Wide and
# Fullwidth are always two.
SINGLE_COLUMN_WIDTH_CLASSES = frozenset({"Na", "N"})


def every_glyph() -> list[str]:
    glyphs = []
    for use_unicode in (True, False):
        glyphs.append(PieceGlyphs.empty_square_glyph(use_unicode))
        for color in ALL_COLORS:
            for piece_type in HOLLOW_UNICODE_GLYPHS_BY_PIECE_TYPE:
                for transparent_white in (True, False):
                    glyphs.append(
                        PieceGlyphs.glyph_for(
                            occupant=Occupant(color=color, piece_type=piece_type),
                            use_unicode=use_unicode,
                            transparent_white=transparent_white,
                        )
                    )
    return glyphs


class GlyphWidthTest(unittest.TestCase):
    def test_no_glyph_is_ambiguous_or_wide(self) -> None:
        for glyph in every_glyph():
            with self.subTest(glyph=glyph, codepoint=f"U+{ord(glyph):04X}"):
                width_class = unicodedata.east_asian_width(glyph)
                self.assertIn(
                    width_class,
                    SINGLE_COLUMN_WIDTH_CLASSES,
                    f"{glyph!r} (U+{ord(glyph):04X}, "
                    f"{unicodedata.name(glyph, '?')}) is width class "
                    f"{width_class!r}, which some terminals draw two columns wide",
                )

    def test_every_glyph_is_a_single_character(self) -> None:
        for glyph in every_glyph():
            with self.subTest(glyph=glyph):
                self.assertEqual(len(glyph), 1)
