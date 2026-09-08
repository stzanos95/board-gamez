import unittest

from chess_cli.config_error import ConfigError
from chess_cli.console.config import ConsoleConfig, ConsoleType, TerminalConsoleConfig
from chess_cli.console.provider import CONSOLE_BUILDERS_BY_TYPE, ConsoleProvider
from chess_cli.console.terminal_console import TerminalConsole
from tests.settings_builder import console_config_for


class ConsoleProviderTest(unittest.TestCase):
    def test_the_terminal_type_builds_a_terminal_console(self) -> None:
        console = ConsoleProvider.get_console(console_config_for())
        self.assertIsInstance(console, TerminalConsole)

    def test_the_console_is_given_its_own_configuration(self) -> None:
        console = ConsoleProvider.get_console(console_config_for(prompt_suffix=" $ "))
        assert isinstance(console, TerminalConsole)
        self.assertEqual(console.config.prompt_suffix, " $ ")

    def test_a_selected_console_with_no_configuration_is_refused(self) -> None:
        with self.assertRaises(ConfigError) as caught:
            ConsoleProvider.get_console(
                ConsoleConfig(console=ConsoleType.TERMINAL, terminal_config=None)
            )
        self.assertIn("terminal_config", str(caught.exception))

    def test_every_console_type_has_a_builder(self) -> None:
        for console_type in ConsoleType:
            with self.subTest(console=console_type):
                self.assertIn(console_type, CONSOLE_BUILDERS_BY_TYPE)

    def test_the_console_appends_its_own_prompt_suffix(self) -> None:
        console = TerminalConsole(config=TerminalConsoleConfig(prompt_suffix=">> "))
        self.assertEqual(console.config.prompt_suffix, ">> ")
