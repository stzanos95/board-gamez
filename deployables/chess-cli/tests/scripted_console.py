"""
A console that plays from a script instead of a terminal.
"""

from dataclasses import dataclass, field

from chess_cli.console.base_console import BaseConsole


@dataclass(slots=True)
class ScriptedConsole(BaseConsole):
    """
    Reads prepared lines and records everything written.

    Mutable, because the script is drawn down as the game consumes it. Running out
    of lines raises EOFError, as a closed terminal would.
    """

    remaining_lines: list[str]
    written_lines: list[str] = field(default_factory=list)
    prompts: list[str] = field(default_factory=list)

    def write_line(self, text: str) -> None:
        self.written_lines.append(text)

    def read_line(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if not self.remaining_lines:
            raise EOFError
        return self.remaining_lines.pop(0)

    @property
    def transcript(self) -> str:
        return "\n".join(self.written_lines)
