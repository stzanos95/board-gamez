import unittest

from chess.board.chess_board_state import ChessBoardState
from chess.models.castling_rights import CastlingRights
from chess.models.castling_side import CastlingSide
from chess.models.color import Color
from chess.models.move_type import MoveType
from chess.models.piece_type import PieceType
from chess.models.square import Square
from chess.rules.legal_move_generator import LegalMoveGenerator
from tests_python.position_builder import black, board_with, white
from tests_python.require import require

WHITE_BACK_RANK = [
    white(PieceType.KING, "e1"),
    white(PieceType.ROOK, "a1"),
    white(PieceType.ROOK, "h1"),
]


def castles(state: ChessBoardState) -> set[str]:
    return {
        require(move.castling_side).value
        for move in LegalMoveGenerator.moves_for_side_to_move(state)
        if move.move_type is MoveType.CASTLE
    }


class CastlingTest(unittest.TestCase):
    def test_both_castles_are_offered_when_nothing_is_in_the_way(self) -> None:
        state = board_with(pieces=WHITE_BACK_RANK, castling_rights=CastlingRights.full())
        self.assertEqual(castles(state), {"kingside", "queenside"})

    def test_no_castle_without_the_right(self) -> None:
        state = board_with(pieces=WHITE_BACK_RANK, castling_rights=CastlingRights.none())
        self.assertEqual(castles(state), set())

    def test_a_piece_in_the_way_blocks_that_side(self) -> None:
        state = board_with(
            pieces=[*WHITE_BACK_RANK, white(PieceType.BISHOP, "f1")],
            castling_rights=CastlingRights.full(),
        )
        self.assertEqual(castles(state), {"queenside"})

    def test_the_queenside_knight_square_must_also_be_empty(self) -> None:
        state = board_with(
            pieces=[*WHITE_BACK_RANK, white(PieceType.KNIGHT, "b1")],
            castling_rights=CastlingRights.full(),
        )
        self.assertEqual(castles(state), {"kingside"})

    def test_a_king_in_check_may_not_castle(self) -> None:
        state = board_with(
            pieces=[*WHITE_BACK_RANK, black(PieceType.ROOK, "e8")],
            castling_rights=CastlingRights.full(),
        )
        self.assertEqual(castles(state), set())

    def test_a_king_may_not_castle_through_an_attacked_square(self) -> None:
        state = board_with(
            pieces=[*WHITE_BACK_RANK, black(PieceType.ROOK, "f8")],
            castling_rights=CastlingRights.full(),
        )
        self.assertEqual(castles(state), {"queenside"})

    def test_a_king_may_not_castle_into_check(self) -> None:
        state = board_with(
            pieces=[*WHITE_BACK_RANK, black(PieceType.ROOK, "g8")],
            castling_rights=CastlingRights.full(),
        )
        self.assertEqual(castles(state), {"queenside"})

    def test_the_queenside_knight_square_may_be_attacked(self) -> None:
        # b1 must be empty, but the king never stands on it, so an enemy bearing
        # on b1 does not prevent the castle.
        state = board_with(
            pieces=[*WHITE_BACK_RANK, black(PieceType.ROOK, "b8")],
            castling_rights=CastlingRights.full(),
        )
        self.assertEqual(castles(state), {"kingside", "queenside"})

    def test_castling_moves_both_king_and_rook(self) -> None:
        state = board_with(pieces=WHITE_BACK_RANK, castling_rights=CastlingRights.full())
        castle = next(
            move
            for move in LegalMoveGenerator.moves_for_side_to_move(state)
            if move.move_type is MoveType.CASTLE and move.castling_side is CastlingSide.KINGSIDE
        )
        after = state.apply(castle)
        self.assertEqual(
            require(after.occupant(Square.from_algebraic("g1"))).piece_type, PieceType.KING
        )
        self.assertEqual(
            require(after.occupant(Square.from_algebraic("f1"))).piece_type, PieceType.ROOK
        )
        self.assertTrue(after.is_empty(Square.from_algebraic("e1")))
        self.assertTrue(after.is_empty(Square.from_algebraic("h1")))

    def test_castling_forfeits_both_rights(self) -> None:
        state = board_with(pieces=WHITE_BACK_RANK, castling_rights=CastlingRights.full())
        castle = next(
            move
            for move in LegalMoveGenerator.moves_for_side_to_move(state)
            if move.move_type is MoveType.CASTLE
        )
        after = state.apply(castle)
        self.assertFalse(after.castling_rights.allows(Color.WHITE, CastlingSide.KINGSIDE))
        self.assertFalse(after.castling_rights.allows(Color.WHITE, CastlingSide.QUEENSIDE))

    def test_a_missing_rook_means_no_castle(self) -> None:
        state = board_with(
            pieces=[white(PieceType.KING, "e1")], castling_rights=CastlingRights.full()
        )
        self.assertEqual(castles(state), set())
