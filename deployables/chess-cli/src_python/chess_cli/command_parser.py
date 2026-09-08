"""
Turning a typed line into a command.

Anything that is not a recognised word is taken as an attempted move, and judged
by the part of the system that knows the position.
"""

from chess.core.errors import NotationError

from chess_cli.command import Command
from chess_cli.command_type import CommandType

COMMAND_TYPES_BY_WORD: dict[str, CommandType] = {
    "moves": CommandType.LIST_MOVES,
    "board": CommandType.SHOW_BOARD,
    "history": CommandType.SHOW_HISTORY,
    "undo": CommandType.UNDO,
    "resign": CommandType.RESIGN,
    "help": CommandType.HELP,
    "quit": CommandType.QUIT,
    "exit": CommandType.QUIT,
}


class CommandParser:
    """
    Reading one typed line as a command.
    """

    @staticmethod
    def parse(text: str) -> Command:
        """
        The command this line names.

        Anything that is not a recognised word becomes a MOVE carrying the text
        as typed. Raises NotationError only when nothing was typed at all.
        """
        stripped = text.strip().lower()
        if not stripped:
            raise NotationError(
                f"say a move such as 'e2e4', or one of {', '.join(sorted(COMMAND_TYPES_BY_WORD))}"
            )
        command_type = COMMAND_TYPES_BY_WORD.get(stripped)
        if command_type is not None:
            return Command(command_type=command_type)
        return Command(command_type=CommandType.MOVE, move_text=stripped)
