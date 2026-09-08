"""
Settings and displays for tests, built directly rather than read from a file.
"""

from chess_cli.cli_settings import CliSettings, PlayerSettings
from chess_cli.console.config import ConsoleConfig, ConsoleType, TerminalConsoleConfig
from chess_cli.display.base_display import BaseDisplay
from chess_cli.display.config import DisplayConfig, DisplayType, TextDisplayConfig
from chess_cli.display.provider import DisplayProvider


def display_config_for(
    use_unicode: bool = False,
    show_coordinates: bool = True,
    transparent_white: bool = True,
) -> DisplayConfig:
    return DisplayConfig(
        display=DisplayType.TEXT,
        text_config=TextDisplayConfig(
            use_unicode=use_unicode,
            show_coordinates=show_coordinates,
            transparent_white=transparent_white,
        ),
    )


PROMPT_SUFFIX = "> "


def console_config_for(prompt_suffix: str = PROMPT_SUFFIX) -> ConsoleConfig:
    return ConsoleConfig(
        console=ConsoleType.TERMINAL,
        terminal_config=TerminalConsoleConfig(prompt_suffix=prompt_suffix),
    )


def settings_for(
    white_name: str = "Ada",
    black_name: str = "Alan",
    use_unicode: bool = False,
    show_coordinates: bool = True,
) -> CliSettings:
    return CliSettings(
        players=PlayerSettings(white_name=white_name, black_name=black_name),
        display=display_config_for(use_unicode=use_unicode, show_coordinates=show_coordinates),
        console=console_config_for(),
    )


def display_for(
    use_unicode: bool = False,
    show_coordinates: bool = True,
    transparent_white: bool = True,
) -> BaseDisplay:
    return DisplayProvider.get_display(
        display_config_for(
            use_unicode=use_unicode,
            show_coordinates=show_coordinates,
            transparent_white=transparent_white,
        )
    )
