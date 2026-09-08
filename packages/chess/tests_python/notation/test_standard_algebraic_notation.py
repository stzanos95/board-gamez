import unittest

from chess.board.chess_board_state import ChessBoardState
from chess.board.starting_position import StartingPosition
from chess.models.castling_rights import CastlingRights
from chess.models.piece_type import PieceType
from chess.notation.coordinate_notation import CoordinateNotation
from chess.notation.standard_algebraic_notation import StandardAlgebraicNotation
from chess.rules.game_status_evaluator import GameStatusEvaluator
from chess.rules.legal_move_generator import LegalMoveGenerator
from tests_python.position_builder import black, board_with, white


def san_for(state: ChessBoardState, coordinate_text: str) -> str:
    legal_moves = LegalMoveGenerator.moves_for_side_to_move(state)
    move = CoordinateNotation.find_move(coordinate_text, legal_moves)
    after = state.apply(move)
    resulting_status = GameStatusEvaluator.evaluate(
        state=after,
        position_keys=(),
        legal_moves=LegalMoveGenerator.moves_for_side_to_move(after),
    )
    return StandardAlgebraicNotation.to_text(
        move=move, legal_moves=legal_moves, resulting_status=resulting_status
    ).text


class SimpleNotationTest(unittest.TestCase):
    def test_a_pawn_is_named_by_its_destination(self) -> None:
        self.assertEqual(san_for(StartingPosition.build_state(), "e2e4"), "e4")

    def test_a_piece_is_named_by_its_letter(self) -> None:
        self.assertEqual(san_for(StartingPosition.build_state(), "g1f3"), "Nf3")

    def test_a_capture_is_marked(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.KING, "a1"),
                black(PieceType.KING, "a8"),
                white(PieceType.KNIGHT, "f3"),
                black(PieceType.PAWN, "e5"),
            ]
        )
        self.assertEqual(san_for(state, "f3e5"), "Nxe5")

    def test_a_pawn_capture_names_the_file_it_left(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.KING, "a1"),
                black(PieceType.KING, "a8"),
                white(PieceType.PAWN, "e4"),
                black(PieceType.PAWN, "d5"),
            ]
        )
        self.assertEqual(san_for(state, "e4d5"), "exd5")

    def test_castling(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.KING, "e1"),
                white(PieceType.ROOK, "a1"),
                white(PieceType.ROOK, "h1"),
                black(PieceType.KING, "e8"),
            ],
            castling_rights=CastlingRights.full(),
        )
        self.assertEqual(san_for(state, "e1g1"), "O-O")
        self.assertEqual(san_for(state, "e1c1"), "O-O-O")

    def test_promotion(self) -> None:
        # The black king stands clear of the new queen's lines, so the notation
        # under test is the promotion mark alone rather than a check as well.
        state = board_with(
            pieces=[
                white(PieceType.PAWN, "e7"),
                white(PieceType.KING, "a1"),
                black(PieceType.KING, "a5"),
            ]
        )
        self.assertEqual(san_for(state, "e7e8q"), "e8=Q")
        self.assertEqual(san_for(state, "e7e8n"), "e8=N")

    def test_check_and_mate_are_marked(self) -> None:
        checking = board_with(
            pieces=[
                white(PieceType.KING, "a1"),
                white(PieceType.ROOK, "h2"),
                black(PieceType.KING, "e8"),
            ]
        )
        self.assertEqual(san_for(checking, "h2e2"), "Re2+")
        mating = board_with(
            pieces=[
                white(PieceType.KING, "a1"),
                white(PieceType.ROOK, "h7"),
                white(PieceType.ROOK, "g1"),
                black(PieceType.KING, "e8"),
            ]
        )
        self.assertEqual(san_for(mating, "g1g8"), "Rg8#")


class DisambiguationTest(unittest.TestCase):
    def test_by_file_when_the_files_differ(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.KING, "a1"),
                black(PieceType.KING, "a8"),
                white(PieceType.KNIGHT, "c3"),
                white(PieceType.KNIGHT, "g1"),
            ]
        )
        self.assertEqual(san_for(state, "c3e2"), "Nce2")
        self.assertEqual(san_for(state, "g1e2"), "Nge2")

    def test_by_rank_when_the_files_match(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.KING, "h1"),
                black(PieceType.KING, "h8"),
                white(PieceType.ROOK, "a1"),
                white(PieceType.ROOK, "a5"),
            ]
        )
        self.assertEqual(san_for(state, "a1a3"), "R1a3")
        self.assertEqual(san_for(state, "a5a3"), "R5a3")

    def test_by_whole_square_when_neither_alone_is_enough(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.KING, "h1"),
                black(PieceType.KING, "h6"),
                white(PieceType.QUEEN, "a1"),
                white(PieceType.QUEEN, "d1"),
                white(PieceType.QUEEN, "a4"),
            ]
        )
        self.assertEqual(san_for(state, "a1d4"), "Qa1d4")

    def test_no_disambiguation_when_only_one_piece_can_go(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.KING, "a1"),
                black(PieceType.KING, "a8"),
                white(PieceType.KNIGHT, "c3"),
            ]
        )
        self.assertEqual(san_for(state, "c3e2"), "Ne2")
