import unittest

from idl.chess.model import game_pb2, piece_pb2
from idl.chess.model.game_pb2 import (
    GAME_STATUS_CHECKMATE,
    GAME_STATUS_DRAW_BY_REPETITION,
    GAME_STATUS_IN_PROGRESS,
)
from idl.chess.model.piece_pb2 import COLOR_BLACK, COLOR_WHITE

from chess.core.errors import IllegalMoveError
from chess.engine.chess_engine import ChessEngine
from chess.notation.coordinate_notation import CoordinateNotation
from tests_python.require import require

WHITE_PARTICIPANT = 1
BLACK_PARTICIPANT = 2

SCHOLARS_MATE = ("e2e4", "e7e5", "f1c4", "b8c6", "d1h5", "g8f6", "h5f7")
FOOLS_MATE = ("f2f3", "e7e5", "g2g4", "d8h4")
KNIGHT_SHUFFLE = ("g1f3", "g8f6", "f3g1", "f6g8")


def new_game() -> ChessEngine:
    return ChessEngine.new_game(
        white_participant=WHITE_PARTICIPANT, black_participant=BLACK_PARTICIPANT
    )


def play_all(engine: ChessEngine, texts: tuple[str, ...]) -> ChessEngine:
    for text in texts:
        engine = engine.play(CoordinateNotation.find_move(text, engine.legal_moves))
    return engine


class NewGameTest(unittest.TestCase):
    def test_starts_with_twenty_legal_moves(self) -> None:
        self.assertEqual(len(new_game().legal_moves), 20)

    def test_starts_in_progress_with_white_to_play(self) -> None:
        engine = new_game()
        self.assertEqual(engine.status, GAME_STATUS_IN_PROGRESS)
        self.assertEqual(engine.active_player.participant, WHITE_PARTICIPANT)
        self.assertEqual(engine.active_player.color, piece_pb2.COLOR_WHITE)
        self.assertIsNone(engine.result)
        self.assertFalse(engine.is_over)

    def test_the_opening_position_is_already_recorded(self) -> None:
        engine = new_game()
        self.assertEqual(engine.turns, ())
        self.assertEqual(len(engine.position_keys), 1)

    def test_the_roster_seats_each_participant_by_colour(self) -> None:
        roster = new_game().roster
        self.assertEqual(roster.white.color, piece_pb2.COLOR_WHITE)
        self.assertEqual(roster.white.participant, WHITE_PARTICIPANT)
        self.assertEqual(roster.black.color, piece_pb2.COLOR_BLACK)
        self.assertEqual(roster.black.participant, BLACK_PARTICIPANT)


class PlayTest(unittest.TestCase):
    def test_playing_returns_a_new_game_and_leaves_the_old_one(self) -> None:
        engine = new_game()
        after = play_all(engine, ("e2e4",))
        self.assertEqual(len(engine.turns), 0)
        self.assertEqual(len(after.turns), 1)
        self.assertEqual(engine.state.side_to_move, COLOR_WHITE)
        self.assertEqual(after.state.side_to_move, COLOR_BLACK)

    def test_an_illegal_move_is_refused(self) -> None:
        engine = new_game()
        other = play_all(engine, ("e2e4", "e7e5"))
        with self.assertRaises(IllegalMoveError):
            engine.play(other.turns[-1].move)

    def test_each_turn_records_who_played_and_what_it_is_called(self) -> None:
        engine = play_all(new_game(), ("e2e4", "e7e5", "g1f3"))
        self.assertEqual([turn.notation for turn in engine.turns], ["e4", "e5", "Nf3"])
        self.assertEqual([turn.number for turn in engine.turns], [1, 1, 2])
        self.assertEqual(engine.turns[1].player.participant, BLACK_PARTICIPANT)

    def test_each_turn_records_the_status_it_led_to(self) -> None:
        engine = play_all(new_game(), FOOLS_MATE)
        self.assertEqual(engine.turns[-1].resulting_status, game_pb2.GAME_STATUS_CHECKMATE)
        self.assertEqual(engine.turns[0].resulting_status, game_pb2.GAME_STATUS_IN_PROGRESS)


class TerminationTest(unittest.TestCase):
    def test_scholars_mate(self) -> None:
        engine = play_all(new_game(), SCHOLARS_MATE)
        self.assertEqual(engine.status, GAME_STATUS_CHECKMATE)
        self.assertTrue(engine.is_over)
        self.assertEqual(
            [turn.notation for turn in engine.turns],
            ["e4", "e5", "Bc4", "Nc6", "Qh5", "Nf6", "Qxf7#"],
        )
        result = require(engine.result)
        self.assertEqual(result.outcome, game_pb2.GAME_OUTCOME_WHITE_WINS)
        self.assertEqual(result.winner.participant, WHITE_PARTICIPANT)
        self.assertEqual(result.status, game_pb2.GAME_STATUS_CHECKMATE)
        self.assertFalse(result.HasField("resigning_player"))

    def test_fools_mate_is_won_by_black(self) -> None:
        engine = play_all(new_game(), FOOLS_MATE)
        self.assertEqual(engine.status, GAME_STATUS_CHECKMATE)
        self.assertEqual(require(engine.result).outcome, game_pb2.GAME_OUTCOME_BLACK_WINS)
        self.assertEqual(engine.turns[-1].notation, "Qh4#")

    def test_nothing_can_be_played_after_mate(self) -> None:
        engine = play_all(new_game(), SCHOLARS_MATE)
        with self.assertRaises(IllegalMoveError):
            engine.play(engine.turns[0].move)

    def test_resigning_hands_the_game_to_the_opponent(self) -> None:
        engine = play_all(new_game(), ("e2e4",)).resign(COLOR_BLACK)
        self.assertTrue(engine.is_over)
        self.assertEqual(engine.resigning_color, COLOR_BLACK)
        result = require(engine.result)
        self.assertEqual(result.outcome, game_pb2.GAME_OUTCOME_WHITE_WINS)
        self.assertEqual(result.resigning_player.participant, BLACK_PARTICIPANT)
        self.assertEqual(result.winner.participant, WHITE_PARTICIPANT)
        self.assertEqual(result.status, game_pb2.GAME_STATUS_UNSPECIFIED)

    def test_a_finished_game_cannot_be_resigned_again(self) -> None:
        engine = play_all(new_game(), SCHOLARS_MATE)
        with self.assertRaises(IllegalMoveError):
            engine.resign(COLOR_WHITE)

    def test_shuffling_knights_back_and_forth_draws(self) -> None:
        engine = play_all(new_game(), KNIGHT_SHUFFLE)
        self.assertEqual(engine.status, GAME_STATUS_IN_PROGRESS)
        engine = play_all(engine, KNIGHT_SHUFFLE)
        self.assertEqual(engine.status, GAME_STATUS_DRAW_BY_REPETITION)
        result = require(engine.result)
        self.assertEqual(result.outcome, game_pb2.GAME_OUTCOME_DRAW)
        self.assertEqual(result.status, game_pb2.GAME_STATUS_DRAW_BY_REPETITION)
        self.assertFalse(result.HasField("winner"))


class TakebackTest(unittest.TestCase):
    def test_an_earlier_engine_is_still_a_playable_game(self) -> None:
        opening = new_game()
        later = play_all(opening, SCHOLARS_MATE)
        self.assertTrue(later.is_over)
        self.assertFalse(opening.is_over)
        self.assertEqual(len(opening.legal_moves), 20)
        self.assertEqual(len(play_all(opening, ("d2d4",)).turns), 1)
