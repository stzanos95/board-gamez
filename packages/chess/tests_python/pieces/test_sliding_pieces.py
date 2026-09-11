import unittest

from idl.chess.model.piece_pb2 import (
    COLOR_WHITE,
    PIECE_TYPE_BISHOP,
    PIECE_TYPE_KING,
    PIECE_TYPE_KNIGHT,
    PIECE_TYPE_PAWN,
    PIECE_TYPE_QUEEN,
    PIECE_TYPE_ROOK,
)

from chess.core.move_types import MoveTypes
from chess.core.squares import Squares
from tests_python.position_builder import black, board_with, destinations, white


class BishopTest(unittest.TestCase):
    def test_travels_both_diagonals_from_the_middle(self) -> None:
        bishop = white(PIECE_TYPE_BISHOP, "d4")
        state = board_with(pieces=[bishop])
        self.assertEqual(len(bishop.pseudo_legal_moves(state)), 13)

    def test_stops_short_of_an_ally(self) -> None:
        bishop = white(PIECE_TYPE_BISHOP, "c1")
        state = board_with(pieces=[bishop, white(PIECE_TYPE_PAWN, "e3")])
        self.assertEqual(destinations(bishop.pseudo_legal_moves(state)), {"d2", "b2", "a3"})

    def test_takes_an_enemy_and_goes_no_further(self) -> None:
        bishop = white(PIECE_TYPE_BISHOP, "c1")
        state = board_with(pieces=[bishop, black(PIECE_TYPE_PAWN, "e3")])
        self.assertEqual(destinations(bishop.pseudo_legal_moves(state)), {"d2", "e3", "b2", "a3"})
        capture = next(
            move
            for move in bishop.pseudo_legal_moves(state)
            if Squares.algebraic(move.destination) == "e3"
        )
        self.assertTrue(MoveTypes.is_capture(capture.move_type))
        self.assertEqual(capture.captured_square, Squares.from_algebraic("e3"))

    def test_defends_its_own_pieces(self) -> None:
        bishop = white(PIECE_TYPE_BISHOP, "c1")
        state = board_with(pieces=[bishop, white(PIECE_TYPE_PAWN, "e3")])
        self.assertIn(
            Squares.get_index(Squares.from_algebraic("e3")), bishop.attacked_squares(state)
        )


class RookTest(unittest.TestCase):
    def test_travels_both_ranks_and_files(self) -> None:
        rook = white(PIECE_TYPE_ROOK, "d4")
        state = board_with(pieces=[rook])
        self.assertEqual(len(rook.pseudo_legal_moves(state)), 14)

    def test_is_blocked_in_every_direction(self) -> None:
        rook = white(PIECE_TYPE_ROOK, "d4")
        state = board_with(
            pieces=[
                rook,
                white(PIECE_TYPE_PAWN, "d5"),
                white(PIECE_TYPE_PAWN, "d3"),
                black(PIECE_TYPE_PAWN, "c4"),
                black(PIECE_TYPE_PAWN, "e4"),
            ]
        )
        self.assertEqual(destinations(rook.pseudo_legal_moves(state)), {"c4", "e4"})


class QueenTest(unittest.TestCase):
    def test_combines_rook_and_bishop(self) -> None:
        queen = white(PIECE_TYPE_QUEEN, "d4")
        state = board_with(pieces=[queen])
        self.assertEqual(len(queen.pseudo_legal_moves(state)), 27)

    def test_from_a_corner(self) -> None:
        queen = white(PIECE_TYPE_QUEEN, "a1")
        state = board_with(pieces=[queen])
        self.assertEqual(len(queen.pseudo_legal_moves(state)), 21)


class KnightTest(unittest.TestCase):
    def test_reaches_eight_squares_from_the_middle(self) -> None:
        knight = white(PIECE_TYPE_KNIGHT, "d4")
        state = board_with(pieces=[knight])
        self.assertEqual(
            destinations(knight.pseudo_legal_moves(state)),
            {"c6", "e6", "f5", "f3", "e2", "c2", "b3", "b5"},
        )

    def test_reaches_two_squares_from_a_corner(self) -> None:
        knight = white(PIECE_TYPE_KNIGHT, "a1")
        state = board_with(pieces=[knight])
        self.assertEqual(destinations(knight.pseudo_legal_moves(state)), {"b3", "c2"})

    def test_leaps_over_whatever_is_in_the_way(self) -> None:
        knight = white(PIECE_TYPE_KNIGHT, "b1")
        state = board_with(
            pieces=[knight, white(PIECE_TYPE_PAWN, "b2"), white(PIECE_TYPE_PAWN, "c2")]
        )
        self.assertEqual(destinations(knight.pseudo_legal_moves(state)), {"a3", "c3", "d2"})


class KingTest(unittest.TestCase):
    def test_steps_one_square_in_every_direction(self) -> None:
        king = white(PIECE_TYPE_KING, "d4")
        state = board_with(pieces=[king])
        self.assertEqual(len(king.pseudo_legal_moves(state)), 8)

    def test_offers_no_castle_of_its_own(self) -> None:
        king = white(PIECE_TYPE_KING, "e1")
        state = board_with(pieces=[king, white(PIECE_TYPE_ROOK, "h1")])
        self.assertNotIn("g1", destinations(king.pseudo_legal_moves(state)))

    def test_attacks_squares_it_could_not_move_to(self) -> None:
        king = white(PIECE_TYPE_KING, "e1")
        state = board_with(pieces=[king, white(PIECE_TYPE_PAWN, "e2")])
        self.assertIn(Squares.get_index(Squares.from_algebraic("e2")), king.attacked_squares(state))
        self.assertNotIn("e2", destinations(king.pseudo_legal_moves(state)))


class RelocationTest(unittest.TestCase):
    def test_moving_a_piece_returns_a_new_one(self) -> None:
        bishop = white(PIECE_TYPE_BISHOP, "c1")
        moved = bishop.relocated_to(Squares.from_algebraic("f4"))
        self.assertEqual(Squares.algebraic(moved.square), "f4")
        self.assertEqual(Squares.algebraic(bishop.square), "c1")
        self.assertIs(type(moved), type(bishop))
        self.assertEqual(moved.color, COLOR_WHITE)
