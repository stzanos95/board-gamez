import unittest

from chess.board.chess_board_state import ChessBoardState
from chess.board.position_key_builder import PositionKeyBuilder
from chess.models.color import Color
from chess.models.game_status import GameStatus
from chess.models.piece_type import PieceType
from chess.models.position_key import PositionKey
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
                white(PieceType.KING, "e1"),
                white(PieceType.ROOK, "a1"),
                black(PieceType.KING, "e8"),
                black(PieceType.ROOK, "h8"),
            ]
        )
        self.assertIs(status_of(state), GameStatus.IN_PROGRESS)

    def test_check_is_reported(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.KING, "e1"),
                white(PieceType.QUEEN, "a2"),
                black(PieceType.KING, "e8"),
                black(PieceType.ROOK, "e7"),
            ]
        )
        self.assertIs(status_of(state), GameStatus.CHECK)

    def test_back_rank_mate(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.KING, "g1"),
                white(PieceType.PAWN, "f2"),
                white(PieceType.PAWN, "g2"),
                white(PieceType.PAWN, "h2"),
                black(PieceType.ROOK, "a1"),
                black(PieceType.KING, "e8"),
            ]
        )
        self.assertIs(status_of(state), GameStatus.CHECKMATE)

    def test_stalemate_is_not_checkmate(self) -> None:
        state = board_with(
            pieces=[
                black(PieceType.KING, "a8"),
                white(PieceType.QUEEN, "b6"),
                white(PieceType.KING, "e1"),
            ],
            side_to_move=Color.BLACK,
        )
        self.assertIs(status_of(state), GameStatus.STALEMATE)

    def test_a_mate_beats_the_fifty_move_rule(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.KING, "g1"),
                white(PieceType.PAWN, "f2"),
                white(PieceType.PAWN, "g2"),
                white(PieceType.PAWN, "h2"),
                black(PieceType.ROOK, "a1"),
                black(PieceType.KING, "e8"),
            ],
            halfmove_clock=200,
        )
        self.assertIs(status_of(state), GameStatus.CHECKMATE)


class DrawTest(unittest.TestCase):
    def test_fifty_move_rule(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.KING, "e1"),
                white(PieceType.ROOK, "a1"),
                black(PieceType.KING, "e8"),
                black(PieceType.ROOK, "h8"),
            ],
            halfmove_clock=100,
        )
        self.assertIs(status_of(state), GameStatus.DRAW_BY_FIFTY_MOVE_RULE)

    def test_one_move_short_of_the_fifty_move_rule(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.KING, "e1"),
                white(PieceType.ROOK, "a1"),
                black(PieceType.KING, "e8"),
                black(PieceType.ROOK, "h8"),
            ],
            halfmove_clock=99,
        )
        self.assertIs(status_of(state), GameStatus.IN_PROGRESS)

    def test_bare_kings(self) -> None:
        state = board_with(pieces=[white(PieceType.KING, "e1"), black(PieceType.KING, "e8")])
        self.assertIs(status_of(state), GameStatus.DRAW_BY_INSUFFICIENT_MATERIAL)

    def test_king_and_bishop_against_king(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.KING, "e1"),
                white(PieceType.BISHOP, "c1"),
                black(PieceType.KING, "e8"),
            ]
        )
        self.assertIs(status_of(state), GameStatus.DRAW_BY_INSUFFICIENT_MATERIAL)

    def test_king_and_knight_against_king(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.KING, "e1"),
                white(PieceType.KNIGHT, "b1"),
                black(PieceType.KING, "e8"),
            ]
        )
        self.assertIs(status_of(state), GameStatus.DRAW_BY_INSUFFICIENT_MATERIAL)

    def test_bishops_on_the_same_colour_cannot_mate(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.KING, "e1"),
                white(PieceType.BISHOP, "c1"),
                black(PieceType.KING, "e8"),
                black(PieceType.BISHOP, "f8"),
            ]
        )
        self.assertIs(status_of(state), GameStatus.DRAW_BY_INSUFFICIENT_MATERIAL)

    def test_bishops_on_opposite_colours_are_not_a_draw(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.KING, "e1"),
                white(PieceType.BISHOP, "c1"),
                black(PieceType.KING, "e8"),
                black(PieceType.BISHOP, "c8"),
            ]
        )
        self.assertIs(status_of(state), GameStatus.IN_PROGRESS)

    def test_two_knights_are_not_an_automatic_draw(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.KING, "e1"),
                white(PieceType.KNIGHT, "b1"),
                white(PieceType.KNIGHT, "g1"),
                black(PieceType.KING, "e8"),
            ]
        )
        self.assertIs(status_of(state), GameStatus.IN_PROGRESS)

    def test_a_pawn_is_always_enough_material(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.KING, "e1"),
                white(PieceType.PAWN, "a2"),
                black(PieceType.KING, "e8"),
            ]
        )
        self.assertIs(status_of(state), GameStatus.IN_PROGRESS)

    def test_a_position_seen_three_times_is_a_draw(self) -> None:
        state = board_with(
            pieces=[
                white(PieceType.KING, "e1"),
                white(PieceType.ROOK, "a1"),
                black(PieceType.KING, "e8"),
                black(PieceType.ROOK, "h8"),
            ]
        )
        key = PositionKeyBuilder.build_key_from_state(state)
        self.assertIs(status_of(state, (key, key)), GameStatus.IN_PROGRESS)
        self.assertIs(status_of(state, (key, key, key)), GameStatus.DRAW_BY_REPETITION)
