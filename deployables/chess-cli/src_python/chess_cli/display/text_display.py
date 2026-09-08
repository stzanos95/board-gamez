from dataclasses import dataclass

from chess.board.chess_board_state import ChessBoardState
from chess.engine.chess_engine import ChessEngine
from chess.models.chess_turn_history import ChessTurnHistory

from chess_cli.display.base_display import BaseDisplay
from chess_cli.display.board_renderer import BoardRenderer
from chess_cli.display.config import TextDisplayConfig
from chess_cli.display.move_list_renderer import MoveListRenderer
from chess_cli.display.status_renderer import StatusRenderer


@dataclass(frozen=True, slots=True)
class TextDisplay(BaseDisplay):
    """
    The board as lines of text, for a terminal.
    """

    config: TextDisplayConfig

    def render_board(self, state: ChessBoardState) -> str:
        renderer = BoardRenderer(
            use_unicode=self.config.use_unicode,
            show_coordinates=self.config.show_coordinates,
            transparent_white=self.config.transparent_white,
        )
        return renderer.render(state)

    def render_status(self, engine: ChessEngine) -> str:
        return StatusRenderer.render_status(engine)

    def render_move_list(self, history: ChessTurnHistory) -> str:
        return MoveListRenderer.render(history)
