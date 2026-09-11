import unittest

from idl.chess.model.castling_pb2 import (
    CASTLING_SIDE_KINGSIDE,
    CASTLING_SIDE_QUEENSIDE,
    CastlingSide,
)
from idl.chess.model.move_pb2 import MOVE_TYPE_CASTLE
from idl.chess.model.piece_pb2 import (
    COLOR_WHITE,
    PIECE_TYPE_BISHOP,
    PIECE_TYPE_KING,
    PIECE_TYPE_KNIGHT,
    PIECE_TYPE_ROOK,
)

from chess.board.chess_board_state import ChessBoardState
from chess.core.castling_rights import CastlingRightSets
from chess.core.squares import Squares
from chess.rules.legal_move_generator import LegalMoveGenerator
from tests_python.position_builder import black, board_with, white
from tests_python.require import require

WHITE_BACK_RANK = [
    white(PIECE_TYPE_KING, "e1"),
    white(PIECE_TYPE_ROOK, "a1"),
    white(PIECE_TYPE_ROOK, "h1"),
]


def castles(state: ChessBoardState) -> set[str]:
    return {
        CastlingSide.Name(move.castling_side)
        for move in LegalMoveGenerator.moves_for_side_to_move(state)
        if move.move_type == MOVE_TYPE_CASTLE
    }


class CastlingTest(unittest.TestCase):
    def test_both_castles_are_offered_when_nothing_is_in_the_way(self) -> None:
        state = board_with(pieces=WHITE_BACK_RANK, castling_rights=CastlingRightSets.full())
        self.assertEqual(castles(state), {"CASTLING_SIDE_KINGSIDE", "CASTLING_SIDE_QUEENSIDE"})

    def test_no_castle_without_the_right(self) -> None:
        state = board_with(pieces=WHITE_BACK_RANK, castling_rights=CastlingRightSets.none())
        self.assertEqual(castles(state), set())

    def test_a_piece_in_the_way_blocks_that_side(self) -> None:
        state = board_with(
            pieces=[*WHITE_BACK_RANK, white(PIECE_TYPE_BISHOP, "f1")],
            castling_rights=CastlingRightSets.full(),
        )
        self.assertEqual(castles(state), {"CASTLING_SIDE_QUEENSIDE"})

    def test_the_queenside_knight_square_must_also_be_empty(self) -> None:
        state = board_with(
            pieces=[*WHITE_BACK_RANK, white(PIECE_TYPE_KNIGHT, "b1")],
            castling_rights=CastlingRightSets.full(),
        )
        self.assertEqual(castles(state), {"CASTLING_SIDE_KINGSIDE"})

    def test_a_king_in_check_may_not_castle(self) -> None:
        state = board_with(
            pieces=[*WHITE_BACK_RANK, black(PIECE_TYPE_ROOK, "e8")],
            castling_rights=CastlingRightSets.full(),
        )
        self.assertEqual(castles(state), set())

    def test_a_king_may_not_castle_through_an_attacked_square(self) -> None:
        state = board_with(
            pieces=[*WHITE_BACK_RANK, black(PIECE_TYPE_ROOK, "f8")],
            castling_rights=CastlingRightSets.full(),
        )
        self.assertEqual(castles(state), {"CASTLING_SIDE_QUEENSIDE"})

    def test_a_king_may_not_castle_into_check(self) -> None:
        state = board_with(
            pieces=[*WHITE_BACK_RANK, black(PIECE_TYPE_ROOK, "g8")],
            castling_rights=CastlingRightSets.full(),
        )
        self.assertEqual(castles(state), {"CASTLING_SIDE_QUEENSIDE"})

    def test_the_queenside_knight_square_may_be_attacked(self) -> None:
        # b1 must be empty, but the king never stands on it, so an enemy bearing
        # on b1 does not prevent the castle.
        state = board_with(
            pieces=[*WHITE_BACK_RANK, black(PIECE_TYPE_ROOK, "b8")],
            castling_rights=CastlingRightSets.full(),
        )
        self.assertEqual(castles(state), {"CASTLING_SIDE_KINGSIDE", "CASTLING_SIDE_QUEENSIDE"})

    def test_castling_moves_both_king_and_rook(self) -> None:
        state = board_with(pieces=WHITE_BACK_RANK, castling_rights=CastlingRightSets.full())
        castle = next(
            move
            for move in LegalMoveGenerator.moves_for_side_to_move(state)
            if move.move_type == MOVE_TYPE_CASTLE and move.castling_side == CASTLING_SIDE_KINGSIDE
        )
        after = state.apply(castle)
        self.assertEqual(
            require(after.occupant(Squares.from_algebraic("g1"))).piece_type, PIECE_TYPE_KING
        )
        self.assertEqual(
            require(after.occupant(Squares.from_algebraic("f1"))).piece_type, PIECE_TYPE_ROOK
        )
        self.assertTrue(after.is_empty(Squares.from_algebraic("e1")))
        self.assertTrue(after.is_empty(Squares.from_algebraic("h1")))

    def test_castling_forfeits_both_rights(self) -> None:
        state = board_with(pieces=WHITE_BACK_RANK, castling_rights=CastlingRightSets.full())
        castle = next(
            move
            for move in LegalMoveGenerator.moves_for_side_to_move(state)
            if move.move_type == MOVE_TYPE_CASTLE
        )
        after = state.apply(castle)
        self.assertFalse(
            CastlingRightSets.allows(after.castling_rights, COLOR_WHITE, CASTLING_SIDE_KINGSIDE)
        )
        self.assertFalse(
            CastlingRightSets.allows(after.castling_rights, COLOR_WHITE, CASTLING_SIDE_QUEENSIDE)
        )

    def test_a_missing_rook_means_no_castle(self) -> None:
        state = board_with(
            pieces=[white(PIECE_TYPE_KING, "e1")], castling_rights=CastlingRightSets.full()
        )
        self.assertEqual(castles(state), set())
