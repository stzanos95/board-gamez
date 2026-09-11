import unittest

from idl.chess.model.board_pb2 import PositionKey
from idl.chess.model.game_pb2 import (
    GAME_STATUS_CHECK,
    GAME_STATUS_CHECKMATE,
    GAME_STATUS_DRAW_BY_FIFTY_MOVE_RULE,
    GAME_STATUS_DRAW_BY_INSUFFICIENT_MATERIAL,
    GAME_STATUS_DRAW_BY_REPETITION,
    GAME_STATUS_IN_PROGRESS,
    GAME_STATUS_STALEMATE,
    GameStatus,
)
from idl.chess.model.piece_pb2 import (
    COLOR_BLACK,
    PIECE_TYPE_BISHOP,
    PIECE_TYPE_KING,
    PIECE_TYPE_KNIGHT,
    PIECE_TYPE_PAWN,
    PIECE_TYPE_QUEEN,
    PIECE_TYPE_ROOK,
)

from chess.board.chess_board_state import ChessBoardState
from chess.board.position_key_builder import PositionKeyBuilder
from chess.rules.game_status_evaluator import GameStatusEvaluator
from chess.rules.legal_move_generator import LegalMoveGenerator
from tests_python.position_builder import black, board_with, white


def status_of(state: ChessBoardState, position_keys: tuple[PositionKey, ...] = ()) -> GameStatus:
    return GameStatusEvaluator.evaluate(
        state=state,
        position_keys=position_keys,
        legal_moves=LegalMoveGenerator.moves_for_side_to_move(state),
    )


class TerminationTest(unittest.TestCase):
    def test_an_ordinary_position_is_in_progress(self) -> None:
        state = board_with(
            pieces=[
                white(PIECE_TYPE_KING, "e1"),
                white(PIECE_TYPE_ROOK, "a1"),
                black(PIECE_TYPE_KING, "e8"),
                black(PIECE_TYPE_ROOK, "h8"),
            ]
        )
        self.assertEqual(status_of(state), GAME_STATUS_IN_PROGRESS)

    def test_check_is_reported(self) -> None:
        state = board_with(
            pieces=[
                white(PIECE_TYPE_KING, "e1"),
                white(PIECE_TYPE_QUEEN, "a2"),
                black(PIECE_TYPE_KING, "e8"),
                black(PIECE_TYPE_ROOK, "e7"),
            ]
        )
        self.assertEqual(status_of(state), GAME_STATUS_CHECK)

    def test_back_rank_mate(self) -> None:
        state = board_with(
            pieces=[
                white(PIECE_TYPE_KING, "g1"),
                white(PIECE_TYPE_PAWN, "f2"),
                white(PIECE_TYPE_PAWN, "g2"),
                white(PIECE_TYPE_PAWN, "h2"),
                black(PIECE_TYPE_ROOK, "a1"),
                black(PIECE_TYPE_KING, "e8"),
            ]
        )
        self.assertEqual(status_of(state), GAME_STATUS_CHECKMATE)

    def test_stalemate_is_not_checkmate(self) -> None:
        state = board_with(
            pieces=[
                black(PIECE_TYPE_KING, "a8"),
                white(PIECE_TYPE_QUEEN, "b6"),
                white(PIECE_TYPE_KING, "e1"),
            ],
            side_to_move=COLOR_BLACK,
        )
        self.assertEqual(status_of(state), GAME_STATUS_STALEMATE)

    def test_a_mate_beats_the_fifty_move_rule(self) -> None:
        state = board_with(
            pieces=[
                white(PIECE_TYPE_KING, "g1"),
                white(PIECE_TYPE_PAWN, "f2"),
                white(PIECE_TYPE_PAWN, "g2"),
                white(PIECE_TYPE_PAWN, "h2"),
                black(PIECE_TYPE_ROOK, "a1"),
                black(PIECE_TYPE_KING, "e8"),
            ],
            halfmove_clock=200,
        )
        self.assertEqual(status_of(state), GAME_STATUS_CHECKMATE)


class DrawTest(unittest.TestCase):
    def test_fifty_move_rule(self) -> None:
        state = board_with(
            pieces=[
                white(PIECE_TYPE_KING, "e1"),
                white(PIECE_TYPE_ROOK, "a1"),
                black(PIECE_TYPE_KING, "e8"),
                black(PIECE_TYPE_ROOK, "h8"),
            ],
            halfmove_clock=100,
        )
        self.assertEqual(status_of(state), GAME_STATUS_DRAW_BY_FIFTY_MOVE_RULE)

    def test_one_move_short_of_the_fifty_move_rule(self) -> None:
        state = board_with(
            pieces=[
                white(PIECE_TYPE_KING, "e1"),
                white(PIECE_TYPE_ROOK, "a1"),
                black(PIECE_TYPE_KING, "e8"),
                black(PIECE_TYPE_ROOK, "h8"),
            ],
            halfmove_clock=99,
        )
        self.assertEqual(status_of(state), GAME_STATUS_IN_PROGRESS)

    def test_bare_kings(self) -> None:
        state = board_with(pieces=[white(PIECE_TYPE_KING, "e1"), black(PIECE_TYPE_KING, "e8")])
        self.assertEqual(status_of(state), GAME_STATUS_DRAW_BY_INSUFFICIENT_MATERIAL)

    def test_king_and_bishop_against_king(self) -> None:
        state = board_with(
            pieces=[
                white(PIECE_TYPE_KING, "e1"),
                white(PIECE_TYPE_BISHOP, "c1"),
                black(PIECE_TYPE_KING, "e8"),
            ]
        )
        self.assertEqual(status_of(state), GAME_STATUS_DRAW_BY_INSUFFICIENT_MATERIAL)

    def test_king_and_knight_against_king(self) -> None:
        state = board_with(
            pieces=[
                white(PIECE_TYPE_KING, "e1"),
                white(PIECE_TYPE_KNIGHT, "b1"),
                black(PIECE_TYPE_KING, "e8"),
            ]
        )
        self.assertEqual(status_of(state), GAME_STATUS_DRAW_BY_INSUFFICIENT_MATERIAL)

    def test_bishops_on_the_same_colour_cannot_mate(self) -> None:
        state = board_with(
            pieces=[
                white(PIECE_TYPE_KING, "e1"),
                white(PIECE_TYPE_BISHOP, "c1"),
                black(PIECE_TYPE_KING, "e8"),
                black(PIECE_TYPE_BISHOP, "f8"),
            ]
        )
        self.assertEqual(status_of(state), GAME_STATUS_DRAW_BY_INSUFFICIENT_MATERIAL)

    def test_bishops_on_opposite_colours_are_not_a_draw(self) -> None:
        state = board_with(
            pieces=[
                white(PIECE_TYPE_KING, "e1"),
                white(PIECE_TYPE_BISHOP, "c1"),
                black(PIECE_TYPE_KING, "e8"),
                black(PIECE_TYPE_BISHOP, "c8"),
            ]
        )
        self.assertEqual(status_of(state), GAME_STATUS_IN_PROGRESS)

    def test_two_knights_are_not_an_automatic_draw(self) -> None:
        state = board_with(
            pieces=[
                white(PIECE_TYPE_KING, "e1"),
                white(PIECE_TYPE_KNIGHT, "b1"),
                white(PIECE_TYPE_KNIGHT, "g1"),
                black(PIECE_TYPE_KING, "e8"),
            ]
        )
        self.assertEqual(status_of(state), GAME_STATUS_IN_PROGRESS)

    def test_a_pawn_is_always_enough_material(self) -> None:
        state = board_with(
            pieces=[
                white(PIECE_TYPE_KING, "e1"),
                white(PIECE_TYPE_PAWN, "a2"),
                black(PIECE_TYPE_KING, "e8"),
            ]
        )
        self.assertEqual(status_of(state), GAME_STATUS_IN_PROGRESS)

    def test_a_position_seen_three_times_is_a_draw(self) -> None:
        state = board_with(
            pieces=[
                white(PIECE_TYPE_KING, "e1"),
                white(PIECE_TYPE_ROOK, "a1"),
                black(PIECE_TYPE_KING, "e8"),
                black(PIECE_TYPE_ROOK, "h8"),
            ]
        )
        key = PositionKeyBuilder.build_key_from_state(state)
        self.assertEqual(status_of(state, (key, key)), GAME_STATUS_IN_PROGRESS)
        self.assertEqual(status_of(state, (key, key, key)), GAME_STATUS_DRAW_BY_REPETITION)
