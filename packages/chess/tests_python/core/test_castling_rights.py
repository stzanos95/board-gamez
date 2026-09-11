import unittest

from idl.chess.model.castling_pb2 import (
    CASTLING_SIDE_KINGSIDE,
    CASTLING_SIDE_QUEENSIDE,
    CastlingRight,
    CastlingRights,
)
from idl.chess.model.piece_pb2 import COLOR_BLACK, COLOR_WHITE

from chess.core.castling_rights import ALL_CASTLING_SIDES, CastlingRightSets
from chess.core.colors import ALL_COLORS


class CastlingRightsTest(unittest.TestCase):
    def test_full_grants_all_four(self) -> None:
        rights = CastlingRightSets.full()
        for color in ALL_COLORS:
            for side in ALL_CASTLING_SIDES:
                self.assertTrue(CastlingRightSets.allows(rights, color, side))

    def test_none_grants_nothing(self) -> None:
        rights = CastlingRightSets.none()
        self.assertFalse(CastlingRightSets.allows(rights, COLOR_WHITE, CASTLING_SIDE_KINGSIDE))

    def test_removing_one_right_leaves_the_others(self) -> None:
        rights = CastlingRightSets.without(
            CastlingRightSets.full(),
            CastlingRight(color=COLOR_WHITE, side=CASTLING_SIDE_KINGSIDE),
        )
        self.assertFalse(CastlingRightSets.allows(rights, COLOR_WHITE, CASTLING_SIDE_KINGSIDE))
        self.assertTrue(CastlingRightSets.allows(rights, COLOR_WHITE, CASTLING_SIDE_QUEENSIDE))
        self.assertTrue(CastlingRightSets.allows(rights, COLOR_BLACK, CASTLING_SIDE_KINGSIDE))

    def test_removing_a_colour_leaves_the_opponent(self) -> None:
        rights = CastlingRightSets.without_color(CastlingRightSets.full(), COLOR_WHITE)
        self.assertFalse(CastlingRightSets.allows(rights, COLOR_WHITE, CASTLING_SIDE_QUEENSIDE))
        self.assertTrue(CastlingRightSets.allows(rights, COLOR_BLACK, CASTLING_SIDE_QUEENSIDE))

    def test_removing_does_not_alter_the_original(self) -> None:
        rights = CastlingRightSets.full()
        CastlingRightSets.without_color(rights, COLOR_WHITE)
        self.assertTrue(CastlingRightSets.allows(rights, COLOR_WHITE, CASTLING_SIDE_KINGSIDE))

    def test_the_same_rights_in_any_order_are_one_message(self) -> None:
        shuffled = CastlingRights(
            available=[
                CastlingRight(color=COLOR_BLACK, side=CASTLING_SIDE_QUEENSIDE),
                CastlingRight(color=COLOR_WHITE, side=CASTLING_SIDE_KINGSIDE),
                CastlingRight(color=COLOR_WHITE, side=CASTLING_SIDE_KINGSIDE),
            ]
        )
        self.assertEqual(
            CastlingRightSets.canonical(shuffled),
            CastlingRights(
                available=[
                    CastlingRight(color=COLOR_WHITE, side=CASTLING_SIDE_KINGSIDE),
                    CastlingRight(color=COLOR_BLACK, side=CASTLING_SIDE_QUEENSIDE),
                ]
            ),
        )
