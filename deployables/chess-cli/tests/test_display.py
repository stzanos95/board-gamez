import unittest

from chess.board.starting_position import StartingPosition
from chess.engine.chess_engine import ChessEngine
from chess.notation.coordinate_notation import CoordinateNotation
from idl.chess.model.piece_pb2 import COLOR_BLACK

from chess_cli.config_error import ConfigError
from chess_cli.display.config import DisplayConfig, DisplayType
from chess_cli.display.provider import DISPLAY_BUILDERS_BY_TYPE, DisplayProvider
from chess_cli.display.text_display import TextDisplay
from chess_cli.player_names import BLACK_PARTICIPANT, WHITE_PARTICIPANT, PlayerNames
from tests.settings_builder import display_config_for, display_for, settings_for

ASCII_DISPLAY = display_for(use_unicode=False)
UNICODE_DISPLAY = display_for(use_unicode=True)
BARE_DISPLAY = display_for(use_unicode=False, show_coordinates=False)
NAMES = PlayerNames.from_settings(settings_for().players)


def new_game() -> ChessEngine:
    return ChessEngine.new_game(
        white_participant=WHITE_PARTICIPANT, black_participant=BLACK_PARTICIPANT
    )


def play_all(engine: ChessEngine, texts: tuple[str, ...]) -> ChessEngine:
    for text in texts:
        engine = engine.play(CoordinateNotation.find_move(text, engine.legal_moves))
    return engine


class DisplayProviderTest(unittest.TestCase):
    def test_the_text_type_builds_a_text_display(self) -> None:
        display = DisplayProvider.get_display(display_config_for())
        self.assertIsInstance(display, TextDisplay)

    def test_the_display_is_given_its_own_configuration(self) -> None:
        display = DisplayProvider.get_display(display_config_for(use_unicode=True))
        assert isinstance(display, TextDisplay)
        self.assertTrue(display.config.use_unicode)

    def test_a_selected_display_with_no_configuration_is_refused(self) -> None:
        with self.assertRaises(ConfigError) as caught:
            DisplayProvider.get_display(DisplayConfig(display=DisplayType.TEXT, text_config=None))
        self.assertIn("text_config", str(caught.exception))

    def test_every_display_type_has_a_builder(self) -> None:
        for display_type in DisplayType:
            with self.subTest(display=display_type):
                self.assertIn(display_type, DISPLAY_BUILDERS_BY_TYPE)


class TextBoardTest(unittest.TestCase):
    def test_draws_the_opening_position_in_ascii(self) -> None:
        lines = ASCII_DISPLAY.render_board(StartingPosition.build_state()).split("\n")
        self.assertEqual(lines[0], "  a b c d e f g h")
        self.assertEqual(lines[1], "8 r n b q k b n r 8")
        self.assertEqual(lines[2], "7 p p p p p p p p 7")
        self.assertEqual(lines[5], "4 . . . . . . . . 4")
        self.assertEqual(lines[8], "1 R N B Q K B N R 1")
        self.assertEqual(lines[9], "  a b c d e f g h")

    def test_files_are_labelled_above_and_below_and_ranks_on_both_sides(self) -> None:
        lines = ASCII_DISPLAY.render_board(StartingPosition.build_state()).split("\n")
        self.assertEqual(len(lines), 10)
        self.assertEqual(lines[0], lines[-1])
        for line in lines[1:-1]:
            self.assertEqual(line[0], line[-1])

    def test_black_is_at_the_top_and_white_at_the_bottom(self) -> None:
        lines = ASCII_DISPLAY.render_board(StartingPosition.build_state()).split("\n")
        self.assertTrue(lines[1].startswith("8"))
        self.assertTrue(lines[8].startswith("1"))

    def test_coordinates_can_be_turned_off(self) -> None:
        lines = BARE_DISPLAY.render_board(StartingPosition.build_state()).split("\n")
        self.assertEqual(len(lines), 8)
        self.assertEqual(lines[0], "r n b q k b n r")
        self.assertEqual(lines[7], "R N B Q K B N R")

    def test_the_unicode_board_marks_empty_squares_with_a_centred_dot(self) -> None:
        rendered = UNICODE_DISPLAY.render_board(StartingPosition.build_state())
        self.assertIn("∙", rendered)
        self.assertNotIn(".", rendered)

    def test_the_ascii_board_keeps_a_full_stop_for_empty_squares(self) -> None:
        rendered = ASCII_DISPLAY.render_board(StartingPosition.build_state())
        self.assertIn(".", rendered)
        self.assertNotIn("∙", rendered)

    def test_the_unicode_board_uses_figurines(self) -> None:
        rendered = UNICODE_DISPLAY.render_board(StartingPosition.build_state())
        self.assertIn("♔", rendered)
        self.assertIn("♚", rendered)
        self.assertNotIn("K", rendered)

    def test_transparent_white_draws_white_hollow_on_its_home_rank(self) -> None:
        display = display_for(use_unicode=True, transparent_white=True)
        lines = display.render_board(StartingPosition.build_state()).split("\n")
        self.assertIn("♔", lines[8])
        self.assertIn("♚", lines[1])

    def test_opaque_white_swaps_the_two_figurine_sets(self) -> None:
        display = display_for(use_unicode=True, transparent_white=False)
        lines = display.render_board(StartingPosition.build_state()).split("\n")
        self.assertIn("♚", lines[8])
        self.assertIn("♔", lines[1])

    def test_a_move_shows_up_on_the_board(self) -> None:
        engine = play_all(new_game(), ("e2e4",))
        lines = ASCII_DISPLAY.render_board(engine.state).split("\n")
        self.assertEqual(lines[5], "4 . . . . P . . . 4")
        self.assertEqual(lines[7], "2 P P P P . P P P 2")


class MoveListTest(unittest.TestCase):
    def test_an_unplayed_game_has_no_move_list(self) -> None:
        self.assertEqual(ASCII_DISPLAY.render_move_list(new_game().turns), "")

    def test_moves_are_numbered_in_pairs(self) -> None:
        engine = play_all(new_game(), ("e2e4", "e7e5", "g1f3", "b8c6"))
        self.assertEqual(ASCII_DISPLAY.render_move_list(engine.turns), "1. e4 e5 2. Nf3 Nc6")

    def test_a_lone_white_move_is_still_numbered(self) -> None:
        engine = play_all(new_game(), ("e2e4",))
        self.assertEqual(ASCII_DISPLAY.render_move_list(engine.turns), "1. e4")


class StatusTest(unittest.TestCase):
    def test_a_quiet_position_says_nothing(self) -> None:
        self.assertEqual(ASCII_DISPLAY.render_status(new_game(), NAMES), "")

    def test_check_names_the_player_who_must_answer_it(self) -> None:
        # 1. e4 d5 2. Bb5+ — the d-pawn has left, so the bishop reaches e8.
        engine = play_all(new_game(), ("e2e4", "d7d5", "f1b5"))
        self.assertEqual(ASCII_DISPLAY.render_status(engine, NAMES), "Alan is in check.")

    def test_checkmate_names_the_winner(self) -> None:
        engine = play_all(new_game(), ("f2f3", "e7e5", "g2g4", "d8h4"))
        self.assertEqual(ASCII_DISPLAY.render_status(engine, NAMES), "Checkmate. Alan wins. 0-1")

    def test_resignation_is_described_as_such(self) -> None:
        engine = play_all(new_game(), ("e2e4",)).resign(COLOR_BLACK)
        self.assertEqual(ASCII_DISPLAY.render_status(engine, NAMES), "Alan resigns. Ada wins. 1-0")

    def test_a_draw_names_the_rule_that_ended_it(self) -> None:
        shuffle = ("g1f3", "g8f6", "f3g1", "f6g8")
        engine = play_all(play_all(new_game(), shuffle), shuffle)
        self.assertEqual(
            ASCII_DISPLAY.render_status(engine, NAMES), "Draw by threefold repetition. 1/2-1/2"
        )
