"""
Putting cards in a random order that a seed fixes.
"""

from idl.uno.model.card_pb2 import Card

from uno.deck.split_mix import SplitMix64

WORD_MASK = (1 << 64) - 1
SHUFFLE_GAMMA = 0x9E3779B97F4A7C15


class Shuffler:
    """
    A Fisher-Yates shuffle over a SplitMix64 stream.

    The stream is named by the game's seed and by which shuffle of that game
    this is, so the deal and every reshuffle of the discard pile come out
    differently from one seed and the same on every replay.
    """

    @staticmethod
    def shuffle(cards: tuple[Card, ...], seed: int, shuffle_number: int) -> tuple[Card, ...]:
        generator = SplitMix64((seed + shuffle_number * SHUFFLE_GAMMA) & WORD_MASK)
        shuffled = list(cards)
        for index in range(len(shuffled) - 1, 0, -1):
            other = generator.next_below(index + 1)
            shuffled[index], shuffled[other] = shuffled[other], shuffled[index]
        return tuple(shuffled)
