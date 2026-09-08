from dataclasses import dataclass

from chess_cli.command_type import CommandType


@dataclass(frozen=True, slots=True)
class Command:
    """
    One instruction typed at the prompt.

    `move_text` is set only for MOVE and holds the text as typed. Whether it names
    a legal move is decided by the engine.
    """

    command_type: CommandType
    move_text: str | None = None
