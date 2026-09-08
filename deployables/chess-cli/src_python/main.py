"""
Entry point for the chess terminal game.

Reads the configuration file named on the command line, builds the display and
console from it, and runs the game.
"""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from chess_cli.cli_settings import CliSettings
from chess_cli.config_error import ConfigError
from chess_cli.console.provider import ConsoleProvider
from chess_cli.display.provider import DisplayProvider
from chess_cli.terminal_game import TerminalGame

EXIT_SUCCESS = 0
EXIT_CONFIG_ERROR = 2

PROGRAM_NAME = "chess-cli"
CONFIG_OPTION = "--config"
CONFIG_DIRECTORY_NAME = "config"
CONFIG_FILE_NAME = "chess_cli.yaml"
DEFAULT_CONFIG_PATH = (
    Path(__file__).resolve().parent.parent / CONFIG_DIRECTORY_NAME / CONFIG_FILE_NAME
)


class ChessCliApplication:
    """
    Wiring the app together from one configuration file.
    """

    @staticmethod
    def run(argv: Sequence[str] | None) -> int:
        """
        Play one game, returning the process exit code.

        Reports a bad configuration on stderr and exits without starting, since
        there is nothing sensible to fall back to.
        """
        arguments = ChessCliApplication._parse_arguments(argv)
        try:
            settings = CliSettings.from_yaml_file(arguments.config)
            display = DisplayProvider.get_display(settings.display)
            console = ConsoleProvider.get_console(settings.console)
        except ConfigError as error:
            print(error, file=sys.stderr)
            return EXIT_CONFIG_ERROR
        TerminalGame(settings=settings, console=console, display=display).play()
        return EXIT_SUCCESS

    @staticmethod
    def _parse_arguments(argv: Sequence[str] | None) -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            prog=PROGRAM_NAME, description="Play chess in the terminal."
        )
        parser.add_argument(
            CONFIG_OPTION,
            type=Path,
            default=DEFAULT_CONFIG_PATH,
            help=f"settings file to bring the app up from (default: {DEFAULT_CONFIG_PATH})",
        )
        return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """
    The console-script entry point, which must be a module-level function.
    """
    return ChessCliApplication.run(argv)


if __name__ == "__main__":
    sys.exit(main())
