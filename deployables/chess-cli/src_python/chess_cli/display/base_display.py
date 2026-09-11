from abc import ABC, abstractmethod

from chess.board.chess_board_state import ChessBoardState
from chess.engine.chess_engine import ChessEngine
from idl.chess.model.game_pb2 import ChessTurn

from chess_cli.player_names import PlayerNames


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
    def render_status(self, engine: ChessEngine, names: PlayerNames) -> str:
        """
        Where the game stands, or an empty string if there is nothing to say.
        """

    @abstractmethod
    def render_move_list(self, turns: tuple[ChessTurn, ...]) -> str:
        """
        The moves played so far, or an empty string if there are none.
        """
