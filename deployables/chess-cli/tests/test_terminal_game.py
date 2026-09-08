import unittest

from chess.models.game_outcome import GameOutcome
from chess.models.game_result import GameResult

from chess_cli.terminal_game import (
    GOODBYE_TEXT,
    NOTHING_TO_UNDO_TEXT,
    TerminalGame,
)
from tests.require import require
from tests.scripted_console import ScriptedConsole
from tests.settings_builder import display_for, settings_for

SETTINGS = settings_for()
DISPLAY = display_for()
SCHOLARS_MATE = ["e2e4", "e7e5", "f1c4", "b8c6", "d1h5", "g8f6", "h5f7"]


def run(lines: list[str]) -> tuple[ScriptedConsole, GameResult | None]:
    console = ScriptedConsole(remaining_lines=list(lines))
    result = TerminalGame(settings=SETTINGS, console=console, display=DISPLAY).play()
    return console, result


class GamePlayTest(unittest.TestCase):
    def test_a_full_game_ends_in_mate(self) -> None:
        console, result = run(SCHOLARS_MATE)
        self.assertIsNotNone(result)
        self.assertIs(require(result).outcome, GameOutcome.WHITE_WINS)
        self.assertIn("Checkmate. Ada wins. 1-0", console.transcript)

    def test_the_board_is_drawn_before_the_first_move(self) -> None:
        console, _ = run(["quit"])
        self.assertIn("8 r n b q k b n r", console.transcript)
        self.assertIn("  a b c d e f g h", console.transcript)

    def test_the_prompt_names_the_player_to_move(self) -> None:
        console, _ = run(["e2e4", "quit"])
        self.assertEqual(console.prompts[0], "Ada (white) ")
        self.assertEqual(console.prompts[1], "Alan (black) ")

    def test_an_illegal_move_is_reported_and_the_turn_is_kept(self) -> None:
        console, _ = run(["e2e5", "quit"])
        self.assertIn("not legal", console.transcript)
        self.assertEqual(console.prompts[1], "Ada (white) ")

    def test_nonsense_is_reported_and_the_turn_is_kept(self) -> None:
        console, _ = run(["banana", "quit"])
        self.assertEqual(console.prompts[1], "Ada (white) ")

    def test_an_empty_line_is_reported_and_the_turn_is_kept(self) -> None:
        console, _ = run(["", "quit"])
        self.assertEqual(console.prompts[1], "Ada (white) ")


class CommandTest(unittest.TestCase):
    def test_quitting_abandons_the_game(self) -> None:
        console, result = run(["quit"])
        self.assertIsNone(result)
        self.assertIn(GOODBYE_TEXT, console.transcript)

    def test_running_out_of_input_abandons_the_game(self) -> None:
        console, result = run([])
        self.assertIsNone(result)
        self.assertIn(GOODBYE_TEXT, console.transcript)

    def test_help_lists_the_commands(self) -> None:
        console, _ = run(["help", "quit"])
        for word in ("moves", "board", "history", "undo", "resign", "quit"):
            self.assertIn(word, console.transcript)

    def test_moves_lists_every_legal_move(self) -> None:
        console, _ = run(["moves", "quit"])
        self.assertIn("e2e4", console.transcript)
        self.assertIn("g1f3", console.transcript)

    def test_history_shows_the_moves_played(self) -> None:
        console, _ = run(["e2e4", "e7e5", "history", "quit"])
        self.assertIn("1. e4 e5", console.transcript)

    def test_undo_takes_a_move_back(self) -> None:
        console, _ = run(["e2e4", "undo", "quit"])
        self.assertEqual(console.prompts[-1], "Ada (white) ")
        self.assertIn("2 P P P P P P P P", console.transcript)

    def test_undo_at_the_start_says_there_is_nothing_to_undo(self) -> None:
        console, _ = run(["undo", "quit"])
        self.assertIn(NOTHING_TO_UNDO_TEXT, console.transcript)

    def test_undo_can_rescue_a_lost_game(self) -> None:
        _console, result = run([*SCHOLARS_MATE[:-1], "undo", "d1h5", "quit"])
        self.assertIsNone(result)

    def test_resigning_ends_the_game(self) -> None:
        console, result = run(["e2e4", "resign"])
        self.assertIsNotNone(result)
        self.assertIs(require(result).outcome, GameOutcome.WHITE_WINS)
        self.assertIn("Alan resigns. Ada wins. 1-0", console.transcript)
