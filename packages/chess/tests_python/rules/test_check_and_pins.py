import unittest

from chess.models.color import Color
from chess.models.piece_type import PieceType
from chess.rules.check_detector import CheckDetector
from chess.rules.legal_move_generator import LegalMoveGenerator
from tests_python.position_builder import black, board_with, destinations, white


class CheckDetectionTest(unittest.TestCase):
    def test_a_rook_on_the_file_gives_check(self) -> None:
        state = board_with(pieces=[white(PieceType.KING, "e1"), black(PieceType.ROOK, "e8")])
        self.assertTrue(CheckDetector.is_in_check(state, Color.WHITE))
        self.assertFalse(CheckDetector.is_in_check(state, Color.BLACK))

    def test_a_blocked_rook_gives_no_check(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.KING, "e1"),
                white(PieceType.PAWN, "e2"),
                black(PieceType.ROOK, "e8"),
            ]
        )
        self.assertFalse(CheckDetector.is_in_check(state, Color.WHITE))

    def test_a_pawn_checks_along_its_diagonal_only(self) -> None:
        diagonal = board_with(pieces=[white(PieceType.KING, "e1"), black(PieceType.PAWN, "d2")])
        self.assertTrue(CheckDetector.is_in_check(diagonal, Color.WHITE))
        ahead = board_with(pieces=[white(PieceType.KING, "e1"), black(PieceType.PAWN, "e2")])
        self.assertFalse(CheckDetector.is_in_check(ahead, Color.WHITE))

    def test_a_position_with_no_king_is_not_in_check(self) -> None:
        state = board_with(pieces=[white(PieceType.ROOK, "a1")])
        self.assertFalse(CheckDetector.is_in_check(state, Color.WHITE))


class LegalityTest(unittest.TestCase):
    def test_a_pinned_piece_cannot_abandon_the_line(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.KING, "e1"),
                white(PieceType.BISHOP, "e2"),
                black(PieceType.ROOK, "e8"),
            ]
        )
        bishop_moves = [
            move
            for move in LegalMoveGenerator.moves_for_side_to_move(state)
            if move.moving_piece_type is PieceType.BISHOP
        ]
        self.assertEqual(bishop_moves, [])

    def test_a_pinned_piece_may_still_move_along_the_line(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.KING, "e1"),
                white(PieceType.ROOK, "e2"),
                black(PieceType.ROOK, "e8"),
            ]
        )
        rook_moves = destinations(
            move
            for move in LegalMoveGenerator.moves_for_side_to_move(state)
            if move.moving_piece_type is PieceType.ROOK
        )
        self.assertEqual(rook_moves, {"e3", "e4", "e5", "e6", "e7", "e8"})

    def test_in_check_only_the_escapes_are_offered(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.KING, "e1"),
                white(PieceType.ROOK, "a2"),
                black(PieceType.ROOK, "e8"),
            ]
        )
        moves = LegalMoveGenerator.moves_for_side_to_move(state)
        self.assertTrue(all(move.destination.algebraic != "a3" for move in moves))
        rook_moves = (move for move in moves if move.moving_piece_type is PieceType.ROOK)
        self.assertIn("e2", destinations(rook_moves))

    def test_a_king_may_not_retreat_along_the_checking_ray(self) -> None:
        # The classic bug: the rook's reach stops at the king, so d1 looks safe
        # until the king actually leaves c1 and the ray runs on.
        state = board_with(pieces=[white(PieceType.KING, "c1"), black(PieceType.ROOK, "a1")])
        king_moves = destinations(
            move
            for move in LegalMoveGenerator.moves_for_side_to_move(state)
            if move.moving_piece_type is PieceType.KING
        )
        self.assertNotIn("d1", king_moves)
        self.assertNotIn("b1", king_moves)
        self.assertEqual(king_moves, {"b2", "c2", "d2"})

    def test_a_king_may_not_step_next_to_the_other_king(self) -> None:
        state = board_with(pieces=[white(PieceType.KING, "e1"), black(PieceType.KING, "e3")])
        king_moves = destinations(LegalMoveGenerator.moves_for_side_to_move(state))
        self.assertEqual(king_moves, {"d1", "f1"})

    def test_a_king_may_take_an_undefended_attacker(self) -> None:
        state = board_with(pieces=[white(PieceType.KING, "e1"), black(PieceType.ROOK, "e2")])
        self.assertIn("e2", destinations(LegalMoveGenerator.moves_for_side_to_move(state)))

    def test_a_king_may_not_take_a_defended_attacker(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.KING, "e1"),
                black(PieceType.ROOK, "e2"),
                black(PieceType.ROOK, "a2"),
            ]
        )
        self.assertNotIn("e2", destinations(LegalMoveGenerator.moves_for_side_to_move(state)))
