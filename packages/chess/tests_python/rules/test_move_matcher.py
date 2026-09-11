import unittest

from idl.chess.model import piece_pb2
from idl.chess.model.move_pb2 import CoordinateMove
from idl.chess.model.piece_pb2 import PIECE_TYPE_KING, PIECE_TYPE_KNIGHT, PIECE_TYPE_PAWN

from chess.board.starting_position import StartingPosition
from chess.core.squares import Squares
from chess.notation.coordinate_notation import CoordinateNotation
from chess.rules.legal_move_generator import LegalMoveGenerator
from chess.rules.move_matcher import MoveMatcher
from tests_python.position_builder import black, board_with, white
from tests_python.require import require

OPENING_MOVES = LegalMoveGenerator.moves_for_side_to_move(StartingPosition.build_state())


class MoveMatcherTest(unittest.TestCase):
    def test_a_named_move_is_found(self) -> None:
        move = require(
            MoveMatcher.get_legal_move(CoordinateNotation.parse_text("e2e4"), OPENING_MOVES)
        )
        self.assertEqual(Squares.algebraic(move.origin), "e2")
        self.assertEqual(Squares.algebraic(move.destination), "e4")

    def test_a_move_the_position_does_not_allow_is_none(self) -> None:
        self.assertIsNone(
            MoveMatcher.get_legal_move(CoordinateNotation.parse_text("e2e5"), OPENING_MOVES)
        )

    def test_an_empty_coordinate_move_is_none(self) -> None:
        self.assertIsNone(MoveMatcher.get_legal_move(CoordinateMove(), OPENING_MOVES))

    def test_a_promotion_needs_its_piece(self) -> None:
        state = board_with(
            pieces=[
                white(PIECE_TYPE_PAWN, "e7"),
                white(PIECE_TYPE_KING, "a1"),
                black(PIECE_TYPE_KING, "a8"),
            ]
        )
        legal = LegalMoveGenerator.moves_for_side_to_move(state)
        self.assertIsNone(MoveMatcher.get_legal_move(CoordinateNotation.parse_text("e7e8"), legal))
        knight = require(MoveMatcher.get_legal_move(CoordinateNotation.parse_text("e7e8n"), legal))
        self.assertEqual(knight.promotion_type, PIECE_TYPE_KNIGHT)

    def test_parse_text_carries_the_promotion(self) -> None:
        parsed = CoordinateNotation.parse_text("e7e8q")
        self.assertEqual(parsed.promotion_type, piece_pb2.PIECE_TYPE_QUEEN)
        self.assertEqual(
            CoordinateNotation.parse_text("e2e4").promotion_type, piece_pb2.PIECE_TYPE_UNSPECIFIED
        )
