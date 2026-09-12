import unittest
from collections import Counter

from idl.uno.model.card_pb2 import (
    CARD_COLOR_RED,
    CARD_KIND_NUMBER,
    CARD_KIND_WILD,
    CARD_KIND_WILD_DRAW_FOUR,
)

from uno.deck.deck_builder import DECK_SIZE, DeckBuilder
from uno.deck.shuffler import Shuffler
from uno.deck.split_mix import SplitMix64

RED_ZEROS = 1
RED_FIVES = 2
WILDS = 4
NUMBER_CARDS = 76
SEED = 99
OTHER_SEED = 100
FIRST_SHUFFLE = 1
SECOND_SHUFFLE = 2
# The first three words SplitMix64 answers from seed 0, as every reference
# implementation answers them.
SPLIT_MIX_ZERO_SEED_WORDS = (
    0xE220A8397B1DCDAF,
    0x6E789E6AA1B965F4,
    0x06C45D188009454F,
)


class DeckTest(unittest.TestCase):
    def test_the_deck_holds_one_hundred_and_eight_cards(self) -> None:
        deck = DeckBuilder.build_deck()
        self.assertEqual(len(deck), DECK_SIZE)

    def test_the_deck_is_composed_as_the_box_says(self) -> None:
        deck = DeckBuilder.build_deck()
        kinds = Counter(card.kind for card in deck)
        self.assertEqual(kinds[CARD_KIND_NUMBER], NUMBER_CARDS)
        self.assertEqual(kinds[CARD_KIND_WILD], WILDS)
        self.assertEqual(kinds[CARD_KIND_WILD_DRAW_FOUR], WILDS)
        red_numbers = Counter(
            card.number
            for card in deck
            if card.kind == CARD_KIND_NUMBER and card.color == CARD_COLOR_RED
        )
        self.assertEqual(red_numbers[0], RED_ZEROS)
        self.assertEqual(red_numbers[5], RED_FIVES)

    def test_a_shuffle_is_fixed_by_its_seed(self) -> None:
        deck = DeckBuilder.build_deck()
        first = Shuffler.shuffle(deck, SEED, FIRST_SHUFFLE)
        again = Shuffler.shuffle(deck, SEED, FIRST_SHUFFLE)
        self.assertEqual(first, again)
        self.assertEqual(
            Counter(card.SerializeToString() for card in first),
            Counter(card.SerializeToString() for card in deck),
        )

    def test_another_seed_or_another_shuffle_is_another_order(self) -> None:
        deck = DeckBuilder.build_deck()
        first = Shuffler.shuffle(deck, SEED, FIRST_SHUFFLE)
        self.assertNotEqual(first, Shuffler.shuffle(deck, OTHER_SEED, FIRST_SHUFFLE))
        self.assertNotEqual(first, Shuffler.shuffle(deck, SEED, SECOND_SHUFFLE))

    def test_the_generator_matches_the_reference_sequence(self) -> None:
        generator = SplitMix64(0)
        words = tuple(generator.next_word() for _ in SPLIT_MIX_ZERO_SEED_WORDS)
        self.assertEqual(words, SPLIT_MIX_ZERO_SEED_WORDS)
