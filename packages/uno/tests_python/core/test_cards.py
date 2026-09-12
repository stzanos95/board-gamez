import unittest

from idl.uno.model.card_pb2 import CARD_COLOR_BLUE, CARD_COLOR_RED

from tests_python.game_builder import draw_two, number, skip, wild, wild_draw_four
from uno.core.cards import Cards


class CardsTest(unittest.TestCase):
    def test_a_card_follows_the_active_colour(self) -> None:
        self.assertTrue(
            Cards.follows(number(CARD_COLOR_RED, 3), number(CARD_COLOR_RED, 7), CARD_COLOR_RED)
        )
        self.assertTrue(
            Cards.follows(skip(CARD_COLOR_RED), number(CARD_COLOR_RED, 7), CARD_COLOR_RED)
        )

    def test_a_number_follows_the_same_number_of_another_colour(self) -> None:
        self.assertTrue(
            Cards.follows(number(CARD_COLOR_BLUE, 7), number(CARD_COLOR_RED, 7), CARD_COLOR_RED)
        )
        self.assertFalse(
            Cards.follows(number(CARD_COLOR_BLUE, 3), number(CARD_COLOR_RED, 7), CARD_COLOR_RED)
        )

    def test_an_action_card_follows_the_same_kind_of_another_colour(self) -> None:
        self.assertTrue(
            Cards.follows(draw_two(CARD_COLOR_BLUE), draw_two(CARD_COLOR_RED), CARD_COLOR_RED)
        )
        self.assertFalse(
            Cards.follows(skip(CARD_COLOR_BLUE), draw_two(CARD_COLOR_RED), CARD_COLOR_RED)
        )

    def test_a_wild_follows_anything(self) -> None:
        self.assertTrue(Cards.follows(wild(), number(CARD_COLOR_RED, 7), CARD_COLOR_RED))
        self.assertTrue(Cards.follows(wild_draw_four(), skip(CARD_COLOR_BLUE), CARD_COLOR_BLUE))

    def test_after_a_wild_the_chosen_colour_is_what_is_followed(self) -> None:
        self.assertTrue(Cards.follows(number(CARD_COLOR_BLUE, 1), wild(), CARD_COLOR_BLUE))
        self.assertFalse(Cards.follows(number(CARD_COLOR_RED, 1), wild(), CARD_COLOR_BLUE))

    def test_a_wild_has_no_colour(self) -> None:
        self.assertFalse(Cards.has_color(wild(), CARD_COLOR_RED))
        self.assertTrue(Cards.has_color(number(CARD_COLOR_RED, 0), CARD_COLOR_RED))
