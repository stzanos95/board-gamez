import unittest

from idl.chess.model import game_pb2, piece_pb2

from chess.adapters.game_adapters import GameAdapters
from chess.engine.chess_engine import ChessEngine
from chess.notation.coordinate_notation import CoordinateNotation
from tests_python.require import require

WHITE_PARTICIPANT = 1
BLACK_PARTICIPANT = 2

SCHOLARS_MATE = ("e2e4", "e7e5", "f1c4", "b8c6", "d1h5", "g8f6", "h5f7")
KNIGHT_SHUFFLE = ("g1f3", "g8f6", "f3g1", "f6g8")


def new_game() -> ChessEngine:
    return ChessEngine.new_game(
        white_participant=WHITE_PARTICIPANT, black_participant=BLACK_PARTICIPANT
    )


def play_all(engine: ChessEngine, texts: tuple[str, ...]) -> ChessEngine:
    for text in texts:
        engine = engine.play(CoordinateNotation.find_move(text, engine.legal_moves))
    return engine


def round_trip(engine: ChessEngine) -> ChessEngine:
    return GameAdapters.chess_game_to_engine(GameAdapters.engine_to_chess_game(engine))


class RecordTest(unittest.TestCase):
    def test_a_new_game_is_recorded_in_full(self) -> None:
        game = GameAdapters.engine_to_chess_game(new_game())
        self.assertEqual(game.roster.white.participant, WHITE_PARTICIPANT)
        self.assertEqual(len(game.state.occupancy), 32)
        self.assertEqual(len(game.history.turns), 0)
        self.assertEqual(len(game.history.position_keys), 1)
        self.assertEqual(len(game.legal_moves), 20)
        self.assertEqual(game.status, game_pb2.GAME_STATUS_IN_PROGRESS)
        self.assertEqual(game.resigning_color, piece_pb2.COLOR_UNSPECIFIED)
        self.assertFalse(game.HasField("result"))

    def test_a_finished_game_carries_its_result(self) -> None:
        game = GameAdapters.engine_to_chess_game(play_all(new_game(), SCHOLARS_MATE))
        self.assertEqual(game.status, game_pb2.GAME_STATUS_CHECKMATE)
        self.assertEqual(len(game.legal_moves), 0)
        self.assertTrue(game.HasField("result"))
        self.assertEqual(game.result.outcome, game_pb2.GAME_OUTCOME_WHITE_WINS)

    def test_a_resigned_game_names_the_colour_that_gave_up(self) -> None:
        resigned = play_all(new_game(), ("e2e4",)).resign(piece_pb2.COLOR_BLACK)
        game = GameAdapters.engine_to_chess_game(resigned)
        self.assertEqual(game.resigning_color, piece_pb2.COLOR_BLACK)
        self.assertEqual(game.result.resigning_player.participant, BLACK_PARTICIPANT)


class RoundTripTest(unittest.TestCase):
    def test_a_game_in_progress_keeps_its_position_history_and_moves(self) -> None:
        engine = play_all(new_game(), ("e2e4", "e7e5", "g1f3"))
        rebuilt = round_trip(engine)
        self.assertEqual(rebuilt.roster, engine.roster)
        self.assertEqual(rebuilt.turns, engine.turns)
        self.assertEqual(rebuilt.position_keys, engine.position_keys)
        self.assertEqual(sorted(rebuilt.legal_moves, key=str), sorted(engine.legal_moves, key=str))
        self.assertEqual(rebuilt.status, engine.status)
        self.assertEqual(rebuilt.state.side_to_move, piece_pb2.COLOR_BLACK)
        self.assertIsNone(rebuilt.resigning_color)

    def test_a_rebuilt_game_can_be_played_on(self) -> None:
        engine = round_trip(play_all(new_game(), SCHOLARS_MATE[:-1]))
        finished = play_all(engine, SCHOLARS_MATE[-1:])
        self.assertEqual(finished.status, game_pb2.GAME_STATUS_CHECKMATE)
        self.assertEqual(finished.turns[-1].notation, "Qxf7#")

    def test_the_repetition_rule_sees_the_recorded_positions(self) -> None:
        engine = round_trip(play_all(new_game(), KNIGHT_SHUFFLE))
        self.assertEqual(
            play_all(engine, KNIGHT_SHUFFLE).status, game_pb2.GAME_STATUS_DRAW_BY_REPETITION
        )

    def test_a_finished_game_stays_finished(self) -> None:
        rebuilt = round_trip(play_all(new_game(), SCHOLARS_MATE))
        self.assertTrue(rebuilt.is_over)
        self.assertEqual(require(rebuilt.result).outcome, game_pb2.GAME_OUTCOME_WHITE_WINS)

    def test_a_resignation_survives_a_round_trip(self) -> None:
        rebuilt = round_trip(play_all(new_game(), ("e2e4",)).resign(piece_pb2.COLOR_BLACK))
        self.assertEqual(rebuilt.resigning_color, piece_pb2.COLOR_BLACK)
        self.assertTrue(rebuilt.is_over)

    def test_the_engine_does_not_share_the_record_it_was_read_from(self) -> None:
        game = GameAdapters.engine_to_chess_game(play_all(new_game(), ("e2e4",)))
        engine = GameAdapters.chess_game_to_engine(game)
        game.roster.white.participant = 9
        del game.history.turns[:]
        self.assertEqual(engine.roster.white.participant, WHITE_PARTICIPANT)
        self.assertEqual(len(engine.turns), 1)

    def test_recorded_legal_moves_are_not_trusted(self) -> None:
        game = GameAdapters.engine_to_chess_game(new_game())
        del game.legal_moves[:]
        game.status = game_pb2.GAME_STATUS_CHECKMATE
        engine = GameAdapters.chess_game_to_engine(game)
        self.assertEqual(len(engine.legal_moves), 20)
        self.assertEqual(engine.status, game_pb2.GAME_STATUS_IN_PROGRESS)
