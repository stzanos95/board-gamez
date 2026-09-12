"""
A small generator of pseudo-random numbers, defined by its arithmetic so a
shuffle taken from a seed comes out the same in any language.
"""

WORD_MASK = (1 << 64) - 1
GOLDEN_GAMMA = 0x9E3779B97F4A7C15
MIX_MULTIPLIER_1 = 0xBF58476D1CE4E5B9
MIX_MULTIPLIER_2 = 0x94D049BB133111EB
MIX_SHIFT_1 = 30
MIX_SHIFT_2 = 27
MIX_SHIFT_3 = 31


class SplitMix64:
    """
    SplitMix64. Every call answers the next 64-bit word of the sequence the
    seed names.

    Mutable, because the sequence is drawn down as it is read. One is built per
    shuffle and never handed across a boundary.
    """

    def __init__(self, seed: int) -> None:
        self._state = seed & WORD_MASK

    def next_word(self) -> int:
        self._state = (self._state + GOLDEN_GAMMA) & WORD_MASK
        word = self._state
        word = ((word ^ (word >> MIX_SHIFT_1)) * MIX_MULTIPLIER_1) & WORD_MASK
        word = ((word ^ (word >> MIX_SHIFT_2)) * MIX_MULTIPLIER_2) & WORD_MASK
        return word ^ (word >> MIX_SHIFT_3)

    def next_below(self, bound: int) -> int:
        """
        A number in [0, bound), by reduction of the next word.
        """
        return self.next_word() % bound
