import unittest

from chess.core.errors import NotationError
from chess.models.direction import Direction
from chess.models.square import Square
from chess.models.vector import Vector
from tests_python.require import require


class SquareTest(unittest.TestCase):
    def test_reads_and_writes_algebraic(self) -> None:
        self.assertEqual(Square.from_algebraic("e4").algebraic, "e4")
        self.assertEqual(Square.from_algebraic("a1").algebraic, "a1")
        self.assertEqual(Square.from_algebraic("h8").algebraic, "h8")

    def test_rejects_text_that_is_not_a_square(self) -> None:
        for text in ("", "e", "e44", "z4", "e9"):
            with self.subTest(text=text), self.assertRaises(NotationError):
                Square.from_algebraic(text)

    def test_shifting_stays_on_the_board(self) -> None:
        self.assertEqual(
            require(Square.from_algebraic("e4").shifted(Direction.NORTH.vector)).algebraic,
            "e5",
        )
        self.assertIsNone(Square.from_algebraic("h8").shifted(Direction.NORTH_EAST.vector))
        self.assertIsNone(Square.from_algebraic("a1").shifted(Direction.SOUTH_WEST.vector))

    def test_shifting_far_off_the_board_gives_nothing(self) -> None:
        self.assertIsNone(Square.from_algebraic("e4").shifted(Vector(file_delta=0, rank_delta=9)))

    def test_square_colour_alternates(self) -> None:
        self.assertFalse(Square.from_algebraic("a1").is_light)
        self.assertTrue(Square.from_algebraic("b1").is_light)
        self.assertTrue(Square.from_algebraic("h1").is_light)
        self.assertFalse(Square.from_algebraic("h8").is_light)

    def test_squares_compare_by_value(self) -> None:
        self.assertEqual(Square.from_algebraic("c3"), Square.from_algebraic("c3"))
        self.assertEqual(len({Square.from_algebraic("c3"), Square.from_algebraic("c3")}), 1)
