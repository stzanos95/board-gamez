from abc import ABC, abstractmethod

from chess.board.chess_board_state import ChessBoardState
from chess.engine.chess_engine import ChessEngine
from chess.models.chess_turn_history import ChessTurnHistory


class BaseDisplay(ABC):
    """
    A way of showing a game.

    Everything the player sees comes from here, so the game loop does not know
    whether it is drawing letters or figurines. Implementations render only: they
    read no input and decide nothing.
    """

    @abstractmethod
    def render_board(self, state: ChessBoardState) -> str:
        """
        The position, ready to print.
        """

    @abstractmethod
    def render_status(self, engine: ChessEngine) -> str:
        """
        Where the game stands, or an empty string if there is nothing to say.
        """

    @abstractmethod
    def render_move_list(self, history: ChessTurnHistory) -> str:
        """
        The moves played so far, or an empty string if there are none.
        """
