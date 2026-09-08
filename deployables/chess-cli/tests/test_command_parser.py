import unittest

from chess.core.errors import NotationError

from chess_cli.command_parser import CommandParser
from chess_cli.command_type import CommandType


class CommandParserTest(unittest.TestCase):
    def test_a_word_it_knows_becomes_that_command(self) -> None:
        for text, command_type in (
            ("moves", CommandType.LIST_MOVES),
            ("board", CommandType.SHOW_BOARD),
            ("history", CommandType.SHOW_HISTORY),
            ("undo", CommandType.UNDO),
            ("resign", CommandType.RESIGN),
            ("help", CommandType.HELP),
            ("quit", CommandType.QUIT),
            ("exit", CommandType.QUIT),
        ):
            with self.subTest(text=text):
                self.assertIs(CommandParser.parse(text).command_type, command_type)

    def test_commands_ignore_case_and_surrounding_space(self) -> None:
        self.assertIs(CommandParser.parse("  UNDO ").command_type, CommandType.UNDO)

    def test_anything_else_is_taken_as_an_attempted_move(self) -> None:
        command = CommandParser.parse("e2e4")
        self.assertIs(command.command_type, CommandType.MOVE)
        self.assertEqual(command.move_text, "e2e4")

    def test_nonsense_is_still_offered_as_a_move_for_the_engine_to_judge(self) -> None:
        self.assertIs(CommandParser.parse("banana").command_type, CommandType.MOVE)

    def test_an_empty_line_is_refused(self) -> None:
        for text in ("", "   ", "\t"):
            with self.subTest(text=text), self.assertRaises(NotationError):
                CommandParser.parse(text)
