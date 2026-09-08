import unittest

from chess.models.castling_right import CastlingRight
from chess.models.castling_rights import CastlingRights
from chess.models.castling_side import CastlingSide
from chess.models.color import Color


class CastlingRightsTest(unittest.TestCase):
    def test_full_grants_all_four(self) -> None:
        rights = CastlingRights.full()
        for color in Color:
            for side in CastlingSide:
                self.assertTrue(rights.allows(color, side))

    def test_none_grants_nothing(self) -> None:
        rights = CastlingRights.none()
        self.assertFalse(rights.allows(Color.WHITE, CastlingSide.KINGSIDE))

    def test_removing_one_right_leaves_the_others(self) -> None:
        rights = CastlingRights.full().without(
            CastlingRight(color=Color.WHITE, side=CastlingSide.KINGSIDE)
        )
        self.assertFalse(rights.allows(Color.WHITE, CastlingSide.KINGSIDE))
        self.assertTrue(rights.allows(Color.WHITE, CastlingSide.QUEENSIDE))
        self.assertTrue(rights.allows(Color.BLACK, CastlingSide.KINGSIDE))

    def test_removing_a_colour_leaves_the_opponent(self) -> None:
        rights = CastlingRights.full().without_color(Color.WHITE)
        self.assertFalse(rights.allows(Color.WHITE, CastlingSide.QUEENSIDE))
        self.assertTrue(rights.allows(Color.BLACK, CastlingSide.QUEENSIDE))

    def test_removing_does_not_alter_the_original(self) -> None:
        rights = CastlingRights.full()
        rights.without_color(Color.WHITE)
        self.assertTrue(rights.allows(Color.WHITE, CastlingSide.KINGSIDE))
