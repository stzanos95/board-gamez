import unittest

from chess.models.color import Color
from chess.models.piece_type import PieceType
from chess.models.square import Square
from tests_python.position_builder import black, board_with, destinations, white


class BishopTest(unittest.TestCase):
    def test_travels_both_diagonals_from_the_middle(self) -> None:
        bishop = white(PieceType.BISHOP, "d4")
        state = board_with(pieces=[bishop])
        self.assertEqual(len(bishop.pseudo_legal_moves(state)), 13)

    def test_stops_short_of_an_ally(self) -> None:
        bishop = white(PieceType.BISHOP, "c1")
        state = board_with(pieces=[bishop, white(PieceType.PAWN, "e3")])
        self.assertEqual(destinations(bishop.pseudo_legal_moves(state)), {"d2", "b2", "a3"})

    def test_takes_an_enemy_and_goes_no_further(self) -> None:
        bishop = white(PieceType.BISHOP, "c1")
        state = board_with(pieces=[bishop, black(PieceType.PAWN, "e3")])
        self.assertEqual(destinations(bishop.pseudo_legal_moves(state)), {"d2", "e3", "b2", "a3"})
        capture = next(
            move for move in bishop.pseudo_legal_moves(state) if move.destination.algebraic == "e3"
        )
        self.assertTrue(capture.move_type.is_capture)
        self.assertEqual(capture.captured_square, Square.from_algebraic("e3"))

    def test_defends_its_own_pieces(self) -> None:
        bishop = white(PieceType.BISHOP, "c1")
        state = board_with(pieces=[bishop, white(PieceType.PAWN, "e3")])
        self.assertIn(Square.from_algebraic("e3"), bishop.attacked_squares(state))


class RookTest(unittest.TestCase):
    def test_travels_both_ranks_and_files(self) -> None:
        rook = white(PieceType.ROOK, "d4")
        state = board_with(pieces=[rook])
        self.assertEqual(len(rook.pseudo_legal_moves(state)), 14)

    def test_is_blocked_in_every_direction(self) -> None:
        rook = white(PieceType.ROOK, "d4")
        state = board_with(
            pieces=[
                rook,
                white(PieceType.PAWN, "d5"),
                white(PieceType.PAWN, "d3"),
                black(PieceType.PAWN, "c4"),
                black(PieceType.PAWN, "e4"),
            ]
        )
        self.assertEqual(destinations(rook.pseudo_legal_moves(state)), {"c4", "e4"})


class QueenTest(unittest.TestCase):
    def test_combines_rook_and_bishop(self) -> None:
        queen = white(PieceType.QUEEN, "d4")
        state = board_with(pieces=[queen])
        self.assertEqual(len(queen.pseudo_legal_moves(state)), 27)

    def test_from_a_corner(self) -> None:
        queen = white(PieceType.QUEEN, "a1")
        state = board_with(pieces=[queen])
        self.assertEqual(len(queen.pseudo_legal_moves(state)), 21)


class KnightTest(unittest.TestCase):
    def test_reaches_eight_squares_from_the_middle(self) -> None:
        knight = white(PieceType.KNIGHT, "d4")
        state = board_with(pieces=[knight])
        self.assertEqual(
            destinations(knight.pseudo_legal_moves(state)),
            {"c6", "e6", "f5", "f3", "e2", "c2", "b3", "b5"},
        )

    def test_reaches_two_squares_from_a_corner(self) -> None:
        knight = white(PieceType.KNIGHT, "a1")
        state = board_with(pieces=[knight])
        self.assertEqual(destinations(knight.pseudo_legal_moves(state)), {"b3", "c2"})

    def test_leaps_over_whatever_is_in_the_way(self) -> None:
        knight = white(PieceType.KNIGHT, "b1")
        state = board_with(
            pieces=[knight, white(PieceType.PAWN, "b2"), white(PieceType.PAWN, "c2")]
        )
        self.assertEqual(destinations(knight.pseudo_legal_moves(state)), {"a3", "c3", "d2"})


class KingTest(unittest.TestCase):
    def test_steps_one_square_in_every_direction(self) -> None:
        king = white(PieceType.KING, "d4")
        state = board_with(pieces=[king])
        self.assertEqual(len(king.pseudo_legal_moves(state)), 8)

    def test_offers_no_castle_of_its_own(self) -> None:
        king = white(PieceType.KING, "e1")
        state = board_with(pieces=[king, white(PieceType.ROOK, "h1")])
        self.assertNotIn("g1", destinations(king.pseudo_legal_moves(state)))

    def test_attacks_squares_it_could_not_move_to(self) -> None:
        king = white(PieceType.KING, "e1")
        state = board_with(pieces=[king, white(PieceType.PAWN, "e2")])
        self.assertIn(Square.from_algebraic("e2"), king.attacked_squares(state))
        self.assertNotIn("e2", destinations(king.pseudo_legal_moves(state)))


class RelocationTest(unittest.TestCase):
    def test_moving_a_piece_returns_a_new_one(self) -> None:
        bishop = white(PieceType.BISHOP, "c1")
        moved = bishop.relocated_to(Square.from_algebraic("f4"))
        self.assertEqual(moved.square.algebraic, "f4")
        self.assertEqual(bishop.square.algebraic, "c1")
        self.assertIs(type(moved), type(bishop))
        self.assertIs(moved.color, Color.WHITE)
