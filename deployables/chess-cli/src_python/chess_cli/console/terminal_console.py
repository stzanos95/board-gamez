from dataclasses import dataclass

from chess_cli.console.base_console import BaseConsole
from chess_cli.console.config import TerminalConsoleConfig


@dataclass(frozen=True, slots=True)
class TerminalConsole(BaseConsole):
    """
    The real terminal.
    """

    config: TerminalConsoleConfig

    def write_line(self, text: str) -> None:
        print(text)

    def read_line(self, prompt: str) -> str:
        return input(f"{prompt}{self.config.prompt_suffix}")
