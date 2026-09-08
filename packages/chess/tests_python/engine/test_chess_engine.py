import unittest

from chess.core.errors import ChessError, IllegalMoveError
from chess.engine.chess_engine import ChessEngine
from chess.models.chess_player import ChessPlayer
from chess.models.color import Color
from chess.models.game_outcome import GameOutcome
from chess.models.game_status import GameStatus
from chess.models.player_roster import PlayerRoster
from chess.notation.coordinate_notation import CoordinateNotation
from tests_python.require import require

SCHOLARS_MATE = ("e2e4", "e7e5", "f1c4", "b8c6", "d1h5", "g8f6", "h5f7")
FOOLS_MATE = ("f2f3", "e7e5", "g2g4", "d8h4")
KNIGHT_SHUFFLE = ("g1f3", "g8f6", "f3g1", "f6g8")


def new_game() -> ChessEngine:
    return ChessEngine.new_game(
        white=ChessPlayer(name="Ada", color=Color.WHITE),
        black=ChessPlayer(name="Alan", color=Color.BLACK),
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
        self.assertIs(engine.status, GameStatus.IN_PROGRESS)
        self.assertEqual(engine.active_player.name, "Ada")
        self.assertIsNone(engine.result)
        self.assertFalse(engine.is_over)

    def test_the_opening_position_is_already_recorded(self) -> None:
        engine = new_game()
        self.assertEqual(engine.history.turns, ())
        self.assertEqual(len(engine.history.position_keys), 1)

    def test_players_must_hold_the_colours_they_are_seated_with(self) -> None:
        with self.assertRaises(ChessError):
            PlayerRoster(
                white=ChessPlayer(name="Ada", color=Color.BLACK),
                black=ChessPlayer(name="Alan", color=Color.BLACK),
            )


class PlayTest(unittest.TestCase):
    def test_playing_returns_a_new_game_and_leaves_the_old_one(self) -> None:
        engine = new_game()
        after = play_all(engine, ("e2e4",))
        self.assertEqual(len(engine.history.turns), 0)
        self.assertEqual(len(after.history.turns), 1)
        self.assertIs(engine.state.side_to_move, Color.WHITE)
        self.assertIs(after.state.side_to_move, Color.BLACK)

    def test_an_illegal_move_is_refused(self) -> None:
        engine = new_game()
        other = play_all(engine, ("e2e4", "e7e5"))
        with self.assertRaises(IllegalMoveError):
            engine.play(other.history.turns[-1].move)

    def test_each_turn_records_who_played_and_what_it_is_called(self) -> None:
        engine = play_all(new_game(), ("e2e4", "e7e5", "g1f3"))
        self.assertEqual([turn.notation.text for turn in engine.history.turns], ["e4", "e5", "Nf3"])
        self.assertEqual([turn.number for turn in engine.history.turns], [1, 1, 2])
        self.assertEqual(engine.history.turns[1].player.name, "Alan")


class TerminationTest(unittest.TestCase):
    def test_scholars_mate(self) -> None:
        engine = play_all(new_game(), SCHOLARS_MATE)
        self.assertIs(engine.status, GameStatus.CHECKMATE)
        self.assertTrue(engine.is_over)
        self.assertEqual(
            [turn.notation.text for turn in engine.history.turns],
            ["e4", "e5", "Bc4", "Nc6", "Qh5", "Nf6", "Qxf7#"],
        )
        result = require(engine.result)
        self.assertIs(result.outcome, GameOutcome.WHITE_WINS)
        self.assertEqual(require(result.winner).name, "Ada")
        self.assertEqual(result.outcome.scoreline, "1-0")

    def test_fools_mate_is_won_by_black(self) -> None:
        engine = play_all(new_game(), FOOLS_MATE)
        self.assertIs(engine.status, GameStatus.CHECKMATE)
        self.assertIs(require(engine.result).outcome, GameOutcome.BLACK_WINS)
        self.assertEqual(engine.history.turns[-1].notation.text, "Qh4#")

    def test_nothing_can_be_played_after_mate(self) -> None:
        engine = play_all(new_game(), SCHOLARS_MATE)
        with self.assertRaises(IllegalMoveError):
            engine.play(engine.history.turns[0].move)

    def test_resigning_hands_the_game_to_the_opponent(self) -> None:
        engine = play_all(new_game(), ("e2e4",)).resign()
        self.assertTrue(engine.is_over)
        result = require(engine.result)
        self.assertIs(result.outcome, GameOutcome.WHITE_WINS)
        self.assertEqual(require(result.resigning_player).name, "Alan")
        self.assertEqual(require(result.winner).name, "Ada")
        self.assertIsNone(result.status)

    def test_a_finished_game_cannot_be_resigned_again(self) -> None:
        engine = play_all(new_game(), SCHOLARS_MATE)
        with self.assertRaises(IllegalMoveError):
            engine.resign()

    def test_shuffling_knights_back_and_forth_draws(self) -> None:
        engine = play_all(new_game(), KNIGHT_SHUFFLE)
        self.assertIs(engine.status, GameStatus.IN_PROGRESS)
        engine = play_all(engine, KNIGHT_SHUFFLE)
        self.assertIs(engine.status, GameStatus.DRAW_BY_REPETITION)
        self.assertIs(require(engine.result).outcome, GameOutcome.DRAW)
        self.assertEqual(require(engine.result).outcome.scoreline, "1/2-1/2")


class TakebackTest(unittest.TestCase):
    def test_an_earlier_engine_is_still_a_playable_game(self) -> None:
        opening = new_game()
        later = play_all(opening, SCHOLARS_MATE)
        self.assertTrue(later.is_over)
        self.assertFalse(opening.is_over)
        self.assertEqual(len(opening.legal_moves), 20)
        self.assertEqual(len(play_all(opening, ("d2d4",)).history.turns), 1)
