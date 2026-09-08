"""
Building the console the configuration asked for.

A registry rather than a chain of conditionals: a new console is an entry here and
its own module.
"""

from collections.abc import Callable

from chess_cli.config_error import ConfigError
from chess_cli.console.base_console import BaseConsole
from chess_cli.console.config import ConsoleConfig, ConsoleType
from chess_cli.console.terminal_console import TerminalConsole


class ConsoleProvider:
    """
    The one place a console is constructed.
    """

    @staticmethod
    def get_console(config: ConsoleConfig) -> BaseConsole:
        """
        The console the configuration selects, holding its own settings.

        Raises ConfigError when the selected console has no builder, or when its
        settings section is missing.
        """
        builder = CONSOLE_BUILDERS_BY_TYPE.get(config.console)
        if builder is None:
            raise ConfigError(
                f"no console is registered for {config.console.value!r}; "
                f"known consoles are "
                f"{', '.join(sorted(console.value for console in CONSOLE_BUILDERS_BY_TYPE))}"
            )
        return builder(config)

    @staticmethod
    def _build_terminal_console(config: ConsoleConfig) -> BaseConsole:
        if config.terminal_config is None:
            raise ConfigError(
                f"console is {ConsoleType.TERMINAL.value!r} but terminal_config is "
                f"missing; add a terminal_config section to the configuration file"
            )
        return TerminalConsole(config=config.terminal_config)


# Keys are data — a console type names its builder. This is a lookup, not a
# record. Defined after the class so it can name the static methods above.
CONSOLE_BUILDERS_BY_TYPE: dict[ConsoleType, Callable[[ConsoleConfig], BaseConsole]] = {
    ConsoleType.TERMINAL: ConsoleProvider._build_terminal_console,
}
