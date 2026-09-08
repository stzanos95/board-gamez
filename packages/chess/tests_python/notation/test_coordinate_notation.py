import unittest

from chess.board.starting_position import StartingPosition
from chess.core.errors import IllegalMoveError, NotationError
from chess.models.piece_type import PieceType
from chess.notation.coordinate_notation import CoordinateNotation
from chess.rules.legal_move_generator import LegalMoveGenerator
from tests_python.position_builder import black, board_with, white


class CoordinateNotationTest(unittest.TestCase):
    def test_reads_an_ordinary_move(self) -> None:
        state = StartingPosition.build_state()
        move = CoordinateNotation.find_move(
            "e2e4", LegalMoveGenerator.moves_for_side_to_move(state)
        )
        self.assertEqual(move.origin.algebraic, "e2")
        self.assertEqual(move.destination.algebraic, "e4")

    def test_ignores_surrounding_space_and_case(self) -> None:
        state = StartingPosition.build_state()
        move = CoordinateNotation.find_move(
            "  E2E4 ", LegalMoveGenerator.moves_for_side_to_move(state)
        )
        self.assertEqual(CoordinateNotation.to_text(move), "e2e4")

    def test_rejects_text_that_is_not_a_move(self) -> None:
        state = StartingPosition.build_state()
        legal = LegalMoveGenerator.moves_for_side_to_move(state)
        for text in ("", "e2", "e2e4e6", "hello"):
            with self.subTest(text=text), self.assertRaises(NotationError):
                CoordinateNotation.find_move(text, legal)

    def test_rejects_a_well_formed_move_that_is_not_legal(self) -> None:
        state = StartingPosition.build_state()
        with self.assertRaises(IllegalMoveError):
            CoordinateNotation.find_move("e2e5", LegalMoveGenerator.moves_for_side_to_move(state))

    def test_reads_a_promotion(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.PAWN, "e7"),
                white(PieceType.KING, "a1"),
                black(PieceType.KING, "a8"),
            ]
        )
        move = CoordinateNotation.find_move(
            "e7e8q", LegalMoveGenerator.moves_for_side_to_move(state)
        )
        self.assertIs(move.promotion_type, PieceType.QUEEN)

    def test_underpromotion_is_a_different_move(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.PAWN, "e7"),
                white(PieceType.KING, "a1"),
                black(PieceType.KING, "a8"),
            ]
        )
        legal = LegalMoveGenerator.moves_for_side_to_move(state)
        self.assertIs(CoordinateNotation.find_move("e7e8n", legal).promotion_type, PieceType.KNIGHT)

    def test_a_promotion_without_a_piece_says_so(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.PAWN, "e7"),
                white(PieceType.KING, "a1"),
                black(PieceType.KING, "a8"),
            ]
        )
        legal = LegalMoveGenerator.moves_for_side_to_move(state)
        with self.assertRaises(IllegalMoveError) as caught:
            CoordinateNotation.find_move("e7e8", legal)
        self.assertIn("e7e8q", str(caught.exception))

    def test_writes_what_it_reads(self) -> None:
        state = StartingPosition.build_state()
        for move in LegalMoveGenerator.moves_for_side_to_move(state):
            text = CoordinateNotation.to_text(move)
            with self.subTest(text=text):
                self.assertEqual(
                    CoordinateNotation.find_move(
                        text, LegalMoveGenerator.moves_for_side_to_move(state)
                    ),
                    move,
                )
