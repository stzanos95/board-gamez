from enum import Enum


class CommandType(Enum):
    """
    What the player asked for at the prompt.
    """

    MOVE = "move"
    LIST_MOVES = "list_moves"
    SHOW_BOARD = "show_board"
    SHOW_HISTORY = "show_history"
    UNDO = "undo"
    RESIGN = "resign"
    HELP = "help"
    QUIT = "quit"
