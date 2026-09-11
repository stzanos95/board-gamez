import unittest

from idl.chess.model.piece_pb2 import COLOR_WHITE, PIECE_TYPE_KING, PIECE_TYPE_PAWN, PIECE_TYPE_ROOK

from chess.adapters.board_adapters import BoardAdapters
from chess.board.position_key_builder import PositionKeyBuilder
from chess.board.starting_position import StartingPosition
from chess.core.squares import Squares
from tests_python.position_builder import black, board_with, rights_from_text, white


class BoardStateTest(unittest.TestCase):
    def test_the_opening_position_survives_a_round_trip(self) -> None:
        state = StartingPosition.build_state()
        message = BoardAdapters.state_to_message(state)
        self.assertEqual(len(message.occupancy), 32)
        self.assertEqual(message.side_to_move, COLOR_WHITE)
        self.assertEqual(len(message.castling_rights.available), 4)
        self.assertFalse(message.HasField("en_passant_target"))
        self.assertEqual(message.fullmove_number, 1)

        rebuilt = BoardAdapters.message_to_state(message)
        self.assertEqual(BoardAdapters.state_to_message(rebuilt), message)
        self.assertEqual(
            PositionKeyBuilder.build_key_from_state(rebuilt),
            PositionKeyBuilder.build_key_from_state(state),
        )

    def test_a_position_with_an_en_passant_target_keeps_it(self) -> None:
        state = board_with(
            pieces=[
                white(PIECE_TYPE_KING, "e1"),
                black(PIECE_TYPE_KING, "e8"),
                white(PIECE_TYPE_PAWN, "e5"),
                black(PIECE_TYPE_PAWN, "d5"),
            ],
            en_passant_target="d6",
            halfmove_clock=3,
        )
        message = BoardAdapters.state_to_message(state)
        self.assertTrue(message.HasField("en_passant_target"))
        rebuilt = BoardAdapters.message_to_state(message)
        self.assertEqual(rebuilt.en_passant_target, Squares.from_algebraic("d6"))
        self.assertEqual(rebuilt.halfmove_clock, 3)

    def test_castling_rights_are_read_in_one_order_whatever_order_they_arrive_in(self) -> None:
        state = board_with(
            pieces=[
                white(PIECE_TYPE_KING, "e1"),
                white(PIECE_TYPE_ROOK, "h1"),
                black(PIECE_TYPE_KING, "e8"),
                black(PIECE_TYPE_ROOK, "a8"),
            ],
            castling_rights=rights_from_text("qK"),
        )
        message = BoardAdapters.state_to_message(state)
        self.assertEqual(message.castling_rights, rights_from_text("Kq"))
        rebuilt = BoardAdapters.message_to_state(message)
        self.assertEqual(rebuilt.castling_rights, rights_from_text("Kq"))
