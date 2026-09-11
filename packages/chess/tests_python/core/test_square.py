import unittest

from chess.core.errors import NotationError
from chess.core.squares import Squares
from chess.movement.direction import Direction
from chess.movement.vector import Vector
from tests_python.require import require


class SquareTest(unittest.TestCase):
    def test_reads_and_writes_algebraic(self) -> None:
        for text in ("e4", "a1", "h8"):
            with self.subTest(text=text):
                self.assertEqual(Squares.algebraic(Squares.from_algebraic(text)), text)

    def test_rejects_text_that_is_not_a_square(self) -> None:
        for text in ("", "e", "e44", "z4", "e9"):
            with self.subTest(text=text), self.assertRaises(NotationError):
                Squares.from_algebraic(text)

    def test_shifting_stays_on_the_board(self) -> None:
        self.assertEqual(
            Squares.algebraic(
                require(Squares.shifted(Squares.from_algebraic("e4"), Direction.NORTH.vector))
            ),
            "e5",
        )
        self.assertIsNone(
            Squares.shifted(Squares.from_algebraic("h8"), Direction.NORTH_EAST.vector)
        )
        self.assertIsNone(
            Squares.shifted(Squares.from_algebraic("a1"), Direction.SOUTH_WEST.vector)
        )

    def test_shifting_far_off_the_board_gives_nothing(self) -> None:
        self.assertIsNone(
            Squares.shifted(Squares.from_algebraic("e4"), Vector(file_delta=0, rank_delta=9))
        )

    def test_square_colour_alternates(self) -> None:
        self.assertFalse(Squares.is_light(Squares.from_algebraic("a1")))
        self.assertTrue(Squares.is_light(Squares.from_algebraic("b1")))
        self.assertTrue(Squares.is_light(Squares.from_algebraic("h1")))
        self.assertFalse(Squares.is_light(Squares.from_algebraic("h8")))

    def test_squares_compare_by_value_and_index_uniquely(self) -> None:
        self.assertEqual(Squares.from_algebraic("c3"), Squares.from_algebraic("c3"))
        self.assertEqual(Squares.get_index(Squares.from_algebraic("a1")), 0)
        self.assertEqual(Squares.get_index(Squares.from_algebraic("h8")), 63)
        indexes = {
            Squares.get_index(Squares.from_algebraic(f"{file}{rank}"))
            for file in "abcdefgh"
            for rank in "12345678"
        }
        self.assertEqual(len(indexes), 64)
