import unittest

from chess.board.chess_board_state import ChessBoardState
from chess.board.starting_position import StartingPosition
from chess.core.errors import BoardStateError
from chess.models.castling_rights import CastlingRights
from chess.models.castling_side import CastlingSide
from chess.models.color import Color
from chess.models.move import Move
from chess.models.move_type import MoveType
from chess.models.piece_type import PieceType
from chess.models.square import Square
from chess.rules.legal_move_generator import LegalMoveGenerator
from tests_python.position_builder import black, board_with, white
from tests_python.require import require


def move_named(state: ChessBoardState, text: str) -> Move:
    origin, destination = text[:2], text[2:4]
    for move in LegalMoveGenerator.moves_for_side_to_move(state):
        if move.origin.algebraic == origin and move.destination.algebraic == destination:
            return move
    raise AssertionError(f"{text} is not legal in this position")


class ApplyTest(unittest.TestCase):
    def test_applying_leaves_the_original_alone(self) -> None:
        state = StartingPosition.build_state()
        state.apply(move_named(state, "e2e4"))
        self.assertFalse(state.is_empty(Square.from_algebraic("e2")))
        self.assertEqual(len(state.pieces), 32)

    def test_a_move_relocates_its_piece(self) -> None:
        opening = StartingPosition.build_state()
        state = opening.apply(move_named(opening, "e2e4"))
        self.assertTrue(state.is_empty(Square.from_algebraic("e2")))
        occupant = require(state.occupant(Square.from_algebraic("e4")))
        self.assertIs(occupant.piece_type, PieceType.PAWN)

    def test_the_moved_piece_knows_where_it_now_stands(self) -> None:
        opening = StartingPosition.build_state()
        state = opening.apply(move_named(opening, "e2e4"))
        moved = require(state.piece_at(Square.from_algebraic("e4")))
        self.assertEqual(moved.square.algebraic, "e4")

    def test_the_turn_passes(self) -> None:
        state = StartingPosition.build_state()
        self.assertIs(state.apply(move_named(state, "e2e4")).side_to_move, Color.BLACK)

    def test_a_double_push_sets_the_en_passant_target(self) -> None:
        state = StartingPosition.build_state()
        after = state.apply(move_named(state, "e2e4"))
        self.assertEqual(after.en_passant_target, Square.from_algebraic("e3"))

    def test_the_en_passant_target_lasts_only_one_move(self) -> None:
        state = StartingPosition.build_state()
        after = state.apply(move_named(state, "e2e4"))
        self.assertIsNone(after.apply(move_named(after, "b8c6")).en_passant_target)

    def test_moving_from_an_empty_square_is_refused(self) -> None:
        state = board_with(pieces=[white(PieceType.KING, "e1")])
        stray = Move(
            origin=Square.from_algebraic("a1"),
            destination=Square.from_algebraic("a2"),
            moving_color=Color.WHITE,
            moving_piece_type=PieceType.ROOK,
            move_type=MoveType.QUIET,
        )
        with self.assertRaises(BoardStateError):
            state.apply(stray)


class ClockTest(unittest.TestCase):
    def test_a_quiet_move_advances_the_halfmove_clock(self) -> None:
        state = board_with(
            pieces=[white(PieceType.KING, "e1"), black(PieceType.KING, "e8")], halfmove_clock=7
        )
        after = state.apply(move_named(state, "e1e2"))
        self.assertEqual(after.halfmove_clock, 8)

    def test_a_pawn_move_resets_the_halfmove_clock(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.KING, "e1"),
                black(PieceType.KING, "e8"),
                white(PieceType.PAWN, "a2"),
            ],
            halfmove_clock=30,
        )
        self.assertEqual(state.apply(move_named(state, "a2a3")).halfmove_clock, 0)

    def test_a_capture_resets_the_halfmove_clock(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.KING, "e1"),
                black(PieceType.KING, "e8"),
                white(PieceType.ROOK, "a1"),
                black(PieceType.ROOK, "a7"),
            ],
            halfmove_clock=30,
        )
        self.assertEqual(state.apply(move_named(state, "a1a7")).halfmove_clock, 0)

    def test_the_move_number_advances_after_black_plays(self) -> None:
        state = StartingPosition.build_state()
        after_white = state.apply(move_named(state, "e2e4"))
        self.assertEqual(after_white.fullmove_number, 1)
        self.assertEqual(after_white.apply(move_named(after_white, "e7e5")).fullmove_number, 2)


class CastlingRightsUpdateTest(unittest.TestCase):
    def _board(self) -> ChessBoardState:
        return board_with(
            pieces=[
                white(PieceType.KING, "e1"),
                white(PieceType.ROOK, "a1"),
                white(PieceType.ROOK, "h1"),
                black(PieceType.KING, "e8"),
                black(PieceType.ROOK, "a8"),
                black(PieceType.ROOK, "h8"),
            ],
            castling_rights=CastlingRights.full(),
        )

    def test_moving_the_king_forfeits_both_castles(self) -> None:
        after = self._board().apply(move_named(self._board(), "e1e2"))
        self.assertFalse(after.castling_rights.allows(Color.WHITE, CastlingSide.KINGSIDE))
        self.assertFalse(after.castling_rights.allows(Color.WHITE, CastlingSide.QUEENSIDE))
        self.assertTrue(after.castling_rights.allows(Color.BLACK, CastlingSide.KINGSIDE))

    def test_moving_a_rook_forfeits_only_its_own_side(self) -> None:
        after = self._board().apply(move_named(self._board(), "h1g1"))
        self.assertFalse(after.castling_rights.allows(Color.WHITE, CastlingSide.KINGSIDE))
        self.assertTrue(after.castling_rights.allows(Color.WHITE, CastlingSide.QUEENSIDE))

    def test_capturing_a_rook_on_its_home_square_forfeits_that_castle(self) -> None:
        state = self._board()
        after = state.apply(move_named(state, "a1a8"))
        self.assertFalse(after.castling_rights.allows(Color.BLACK, CastlingSide.QUEENSIDE))
        self.assertTrue(after.castling_rights.allows(Color.BLACK, CastlingSide.KINGSIDE))


class StartingPositionTest(unittest.TestCase):
    def test_has_thirty_two_pieces_and_white_to_move(self) -> None:
        state = StartingPosition.build_state()
        self.assertEqual(len(state.pieces), 32)
        self.assertIs(state.side_to_move, Color.WHITE)

    def test_kings_and_queens_are_placed_correctly(self) -> None:
        state = StartingPosition.build_state()
        self.assertEqual(require(state.king_square(Color.WHITE)).algebraic, "e1")
        self.assertEqual(require(state.king_square(Color.BLACK)).algebraic, "e8")
        for square in ("d1", "d8"):
            occupant = require(state.occupant(Square.from_algebraic(square)))
            self.assertIs(occupant.piece_type, PieceType.QUEEN)

    def test_every_castle_is_available(self) -> None:
        self.assertEqual(len(StartingPosition.build_state().castling_rights.available), 4)
