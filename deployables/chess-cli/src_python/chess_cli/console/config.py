"""
Where the game reads from and writes to, and the settings each option needs.

An enum selects, one config dataclass describes each option, and the container
carries one optional field per option.

Adding a console means adding a member, a config, a class and a registry entry in
`provider`. Nothing existing changes.
"""

from dataclasses import dataclass
from enum import Enum

from mashumaro.mixins.yaml import DataClassYAMLMixin


class ConsoleType(Enum):
    """
    Which console to build.
    """

    TERMINAL = "terminal"


@dataclass(frozen=True, slots=True)
class TerminalConsoleConfig(DataClassYAMLMixin):
    """
    Settings for a real terminal.
    """

    prompt_suffix: str


@dataclass(frozen=True, slots=True)
class ConsoleConfig(DataClassYAMLMixin):
    """
    The chosen console, and the settings for each console that has any.
    """

    console: ConsoleType
    terminal_config: TerminalConsoleConfig | None = None
