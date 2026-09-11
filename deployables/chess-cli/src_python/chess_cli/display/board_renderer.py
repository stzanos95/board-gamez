from dataclasses import dataclass

from chess.board.chess_board_state import ChessBoardState
from chess.core.files import ALL_FILES, Files
from chess.core.ranks import ALL_RANKS, Ranks
from idl.chess.model.square_pb2 import Rank, Square

from chess_cli.display.piece_glyphs import PieceGlyphs

RANK_LABEL_GUTTER = " "
FILE_LABEL_INDENT = "  "
CELL_SEPARATOR = " "


@dataclass(frozen=True, slots=True)
class BoardRenderer:
    """
    Draws a board from White's point of view, rank 8 at the top.
    """

    use_unicode: bool
    show_coordinates: bool
    transparent_white: bool

    def render(self, state: ChessBoardState) -> str:
        """
        The whole board as lines of text.

        With coordinates on, files are labelled above and below and ranks on both
        sides, so a square can be read off from whichever edge is nearer.
        """
        ranks = [self._rank_line(state=state, rank=rank) for rank in reversed(ALL_RANKS)]
        if not self.show_coordinates:
            return "\n".join(ranks)
        file_labels = self._file_label_line()
        return "\n".join([file_labels, *ranks, file_labels])

    def _file_label_line(self) -> str:
        letters = CELL_SEPARATOR.join(Files.letter(file) for file in ALL_FILES)
        return f"{FILE_LABEL_INDENT}{letters}"

    def _rank_line(self, state: ChessBoardState, rank: Rank) -> str:
        cells = CELL_SEPARATOR.join(
            self._cell(state=state, square=Square(file=file, rank=rank)) for file in ALL_FILES
        )
        if not self.show_coordinates:
            return cells
        gutter = RANK_LABEL_GUTTER
        return f"{Ranks.digit(rank)}{gutter}{cells}{gutter}{Ranks.digit(rank)}"

    def _cell(self, state: ChessBoardState, square: Square) -> str:
        occupant = state.occupant(square)
        if occupant is None:
            return PieceGlyphs.empty_square_glyph(self.use_unicode)
        return PieceGlyphs.glyph_for(
            occupant=occupant,
            use_unicode=self.use_unicode,
            transparent_white=self.transparent_white,
        )
