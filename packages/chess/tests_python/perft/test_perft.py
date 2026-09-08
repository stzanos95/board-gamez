import os
import unittest

from chess.board.chess_board_state import ChessBoardState
from chess.rules.legal_move_generator import LegalMoveGenerator
from tests_python.perft.reference_positions import REFERENCE_POSITIONS, PerftPosition
from tests_python.position_builder import board_from_placement

SLOW_TESTS_VARIABLE = "CHESS_SLOW_TESTS"
SLOW_TESTS_ENABLED = os.environ.get(SLOW_TESTS_VARIABLE, "").strip().lower() in (
    "1",
    "true",
    "yes",
    "on",
)
LEAF_DEPTH = 1


def perft(state: ChessBoardState, depth: int) -> int:
    moves = LegalMoveGenerator.moves_for_side_to_move(state)
    if depth == LEAF_DEPTH:
        return len(moves)
    return sum(perft(state.apply(move), depth - 1) for move in moves)


def board_for(position: PerftPosition) -> ChessBoardState:
    return board_from_placement(
        placement=position.placement,
        side_to_move=position.side_to_move,
        castling_text=position.castling_text,
        en_passant_target=position.en_passant_target,
    )


class PerftTest(unittest.TestCase):
    def test_every_reference_position_counts_correctly(self) -> None:
        for position in REFERENCE_POSITIONS:
            state = board_for(position)
            for depth, expected in sorted(position.node_counts.items()):
                if depth >= position.slow_from_depth and not SLOW_TESTS_ENABLED:
                    continue
                with self.subTest(position=position.name, depth=depth):
                    self.assertEqual(perft(state, depth), expected)

    @unittest.skipUnless(
        SLOW_TESTS_ENABLED, f"set {SLOW_TESTS_VARIABLE}=1 to run the deep perft counts"
    )
    def test_the_deep_counts_too(self) -> None:
        for position in REFERENCE_POSITIONS:
            state = board_for(position)
            for depth, expected in sorted(position.node_counts.items()):
                if depth < position.slow_from_depth:
                    continue
                with self.subTest(position=position.name, depth=depth):
                    self.assertEqual(perft(state, depth), expected)
