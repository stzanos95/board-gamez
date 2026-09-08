"""
The prompt loop.

The game keeps every engine it has produced. A move pushes a new game onto the
stack and undo pops it, so nothing has to be reversed.
"""

from dataclasses import dataclass

from chess.core.errors import ChessError, IllegalMoveError, NotationError
from chess.engine.chess_engine import ChessEngine
from chess.models.chess_player import ChessPlayer
from chess.models.color import Color
from chess.models.game_result import GameResult
from chess.notation.coordinate_notation import CoordinateNotation

from chess_cli.cli_settings import CliSettings
from chess_cli.command_parser import CommandParser
from chess_cli.command_type import CommandType
from chess_cli.console.base_console import BaseConsole
from chess_cli.display.base_display import BaseDisplay

WELCOME_TEXT = "Chess. Type a move such as 'e2e4', or 'help' for the other commands."
HELP_TEXT = (
    "Moves are written as the square you leave and the square you reach: e2e4.\n"
    "A promotion adds the new piece: e7e8q.\n"
    "  moves    list every legal move\n"
    "  board    draw the board again\n"
    "  history  show the moves so far\n"
    "  undo     take back the last move\n"
    "  resign   give up the game\n"
    "  quit     leave without finishing"
)
GOODBYE_TEXT = "Goodbye."
NOTHING_TO_UNDO_TEXT = "No moves have been played yet."
NO_MOVES_YET_TEXT = "No moves have been played yet."
MOVE_SEPARATOR = " "
ONLY_THE_OPENING_POSITION = 1


@dataclass(frozen=True, slots=True)
class TerminalGame:
    settings: CliSettings
    console: BaseConsole
    display: BaseDisplay

    def play(self) -> GameResult | None:
        """
        Run the game to its end, or until the player leaves.

        Returns the result if the game finished, and None if it was abandoned.
        """
        games = [self._new_game()]
        self.console.write_line(WELCOME_TEXT)
        self._show(games[-1])

        while True:
            engine = games[-1]
            if engine.is_over:
                return engine.result
            try:
                typed = self.console.read_line(self._prompt(engine))
            except EOFError:
                self.console.write_line(GOODBYE_TEXT)
                return None

            try:
                command = CommandParser.parse(typed)
            except NotationError as error:
                self.console.write_line(str(error))
                continue

            if command.command_type is CommandType.QUIT:
                self.console.write_line(GOODBYE_TEXT)
                return None
            if command.command_type is CommandType.HELP:
                self.console.write_line(HELP_TEXT)
                continue
            if command.command_type is CommandType.SHOW_BOARD:
                self._show(engine)
                continue
            if command.command_type is CommandType.SHOW_HISTORY:
                self.console.write_line(
                    self.display.render_move_list(engine.history) or NO_MOVES_YET_TEXT
                )
                continue
            if command.command_type is CommandType.LIST_MOVES:
                self.console.write_line(self._legal_moves_text(engine))
                continue
            if command.command_type is CommandType.UNDO:
                if len(games) == ONLY_THE_OPENING_POSITION:
                    self.console.write_line(NOTHING_TO_UNDO_TEXT)
                    continue
                games.pop()
                self._show(games[-1])
                continue
            if command.command_type is CommandType.RESIGN:
                games.append(engine.resign())
                self._show(games[-1])
                continue

            played = self._played(engine=engine, command_move_text=command.move_text)
            if played is None:
                continue
            games.append(played)
            self._show(played)

    def _played(self, engine: ChessEngine, command_move_text: str | None) -> ChessEngine | None:
        """
        The game after the typed move, or None if the text named no legal move.
        """
        if command_move_text is None:
            raise ChessError("a move command carried no text to read")
        try:
            move = CoordinateNotation.find_move(
                text=command_move_text, legal_moves=engine.legal_moves
            )
        except (NotationError, IllegalMoveError) as error:
            self.console.write_line(str(error))
            return None
        return engine.play(move)

    def _show(self, engine: ChessEngine) -> None:
        self.console.write_line("")
        self.console.write_line(self.display.render_board(engine.state))
        status = self.display.render_status(engine)
        if status:
            self.console.write_line(status)

    def _prompt(self, engine: ChessEngine) -> str:
        # The console appends its own suffix; naming the player is this layer's job.
        player = engine.active_player
        return f"{player.name} ({player.color.value}) "

    def _legal_moves_text(self, engine: ChessEngine) -> str:
        return MOVE_SEPARATOR.join(
            sorted(CoordinateNotation.to_text(move) for move in engine.legal_moves)
        )

    def _new_game(self) -> ChessEngine:
        return ChessEngine.new_game(
            white=ChessPlayer(name=self.settings.players.white_name, color=Color.WHITE),
            black=ChessPlayer(name=self.settings.players.black_name, color=Color.BLACK),
        )
