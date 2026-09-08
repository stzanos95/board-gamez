import unittest

from chess.models.color import Color
from chess.models.move_type import MoveType
from chess.models.piece_type import PieceType
from chess.models.square import Square
from tests_python.position_builder import black, board_with, destinations, white


class PawnPushTest(unittest.TestCase):
    def test_white_advances_up_the_board(self) -> None:
        pawn = white(PieceType.PAWN, "e2")
        state = board_with(pieces=[pawn])
        self.assertEqual(destinations(pawn.pseudo_legal_moves(state)), {"e3", "e4"})

    def test_black_advances_down_the_board(self) -> None:
        pawn = black(PieceType.PAWN, "e7")
        state = board_with(pieces=[pawn], side_to_move=Color.BLACK)
        self.assertEqual(destinations(pawn.pseudo_legal_moves(state)), {"e6", "e5"})

    def test_double_push_only_from_the_home_rank(self) -> None:
        pawn = white(PieceType.PAWN, "e3")
        state = board_with(pieces=[pawn])
        self.assertEqual(destinations(pawn.pseudo_legal_moves(state)), {"e4"})

    def test_double_push_is_marked_as_such(self) -> None:
        pawn = white(PieceType.PAWN, "e2")
        state = board_with(pieces=[pawn])
        double = next(
            move for move in pawn.pseudo_legal_moves(state) if move.destination.algebraic == "e4"
        )
        self.assertIs(double.move_type, MoveType.DOUBLE_PAWN_PUSH)

    def test_a_blocked_pawn_cannot_move_at_all(self) -> None:
        pawn = white(PieceType.PAWN, "e2")
        state = board_with(pieces=[pawn, black(PieceType.PAWN, "e3")])
        self.assertEqual(pawn.pseudo_legal_moves(state), ())

    def test_a_piece_two_squares_ahead_stops_only_the_double_push(self) -> None:
        pawn = white(PieceType.PAWN, "e2")
        state = board_with(pieces=[pawn, black(PieceType.PAWN, "e4")])
        self.assertEqual(destinations(pawn.pseudo_legal_moves(state)), {"e3"})

    def test_a_pawn_never_captures_straight_ahead(self) -> None:
        pawn = white(PieceType.PAWN, "e4")
        state = board_with(pieces=[pawn, black(PieceType.PAWN, "e5")])
        self.assertEqual(pawn.pseudo_legal_moves(state), ())


class PawnCaptureTest(unittest.TestCase):
    def test_takes_diagonally_forward(self) -> None:
        pawn = white(PieceType.PAWN, "e4")
        state = board_with(pieces=[pawn, black(PieceType.PAWN, "d5"), black(PieceType.PAWN, "f5")])
        self.assertEqual(destinations(pawn.pseudo_legal_moves(state)), {"e5", "d5", "f5"})

    def test_does_not_take_its_own_side(self) -> None:
        pawn = white(PieceType.PAWN, "e4")
        state = board_with(pieces=[pawn, white(PieceType.PAWN, "d5")])
        self.assertEqual(destinations(pawn.pseudo_legal_moves(state)), {"e5"})

    def test_attacks_diagonals_but_not_the_square_ahead(self) -> None:
        pawn = white(PieceType.PAWN, "e4")
        state = board_with(pieces=[pawn])
        attacked = {square.algebraic for square in pawn.attacked_squares(state)}
        self.assertEqual(attacked, {"d5", "f5"})

    def test_an_edge_pawn_attacks_only_inward(self) -> None:
        pawn = white(PieceType.PAWN, "a4")
        state = board_with(pieces=[pawn])
        self.assertEqual({s.algebraic for s in pawn.attacked_squares(state)}, {"b5"})


class EnPassantTest(unittest.TestCase):
    def test_takes_a_pawn_that_has_just_run_past(self) -> None:
        pawn = white(PieceType.PAWN, "e5")
        state = board_with(pieces=[pawn, black(PieceType.PAWN, "d5")], en_passant_target="d6")
        capture = next(
            move for move in pawn.pseudo_legal_moves(state) if move.move_type is MoveType.EN_PASSANT
        )
        self.assertEqual(capture.destination, Square.from_algebraic("d6"))
        self.assertEqual(capture.captured_square, Square.from_algebraic("d5"))

    def test_is_unavailable_without_a_target(self) -> None:
        pawn = white(PieceType.PAWN, "e5")
        state = board_with(pieces=[pawn, black(PieceType.PAWN, "d5")])
        self.assertEqual(destinations(pawn.pseudo_legal_moves(state)), {"e6"})


class PromotionTest(unittest.TestCase):
    def test_offers_all_four_pieces(self) -> None:
        pawn = white(PieceType.PAWN, "e7")
        state = board_with(pieces=[pawn])
        moves = pawn.pseudo_legal_moves(state)
        self.assertEqual(len(moves), 4)
        self.assertEqual(
            {move.promotion_type for move in moves},
            {PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT},
        )

    def test_promotes_by_capturing_too(self) -> None:
        pawn = white(PieceType.PAWN, "e7")
        state = board_with(pieces=[pawn, black(PieceType.ROOK, "d8")])
        captures = [
            move
            for move in pawn.pseudo_legal_moves(state)
            if move.move_type is MoveType.PROMOTION_CAPTURE
        ]
        self.assertEqual(len(captures), 4)

    def test_black_promotes_on_the_first_rank(self) -> None:
        pawn = black(PieceType.PAWN, "e2")
        state = board_with(pieces=[pawn], side_to_move=Color.BLACK)
        moves = pawn.pseudo_legal_moves(state)
        self.assertEqual(len(moves), 4)
        self.assertTrue(all(move.destination.algebraic == "e1" for move in moves))
