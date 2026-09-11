"""
The prompt loop.

The game keeps every engine it has produced. A move pushes a new game onto the
stack and undo pops it, so nothing has to be reversed.
"""

from dataclasses import dataclass

from chess.core.errors import ChessError, IllegalMoveError, NotationError
from chess.engine.chess_engine import ChessEngine
from chess.notation.coordinate_notation import CoordinateNotation
from idl.chess.model.game_pb2 import GameResult
from idl.chess.model.piece_pb2 import COLOR_BLACK, COLOR_WHITE, Color

from chess_cli.cli_settings import CliSettings
from chess_cli.command_parser import CommandParser
from chess_cli.command_type import CommandType
from chess_cli.console.base_console import BaseConsole
from chess_cli.display.base_display import BaseDisplay
from chess_cli.player_names import BLACK_PARTICIPANT, WHITE_PARTICIPANT, PlayerNames

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

SideNamesByColor = dict[Color, str]

SIDE_NAMES_BY_COLOR: SideNamesByColor = {COLOR_WHITE: "white", COLOR_BLACK: "black"}
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
        names = PlayerNames.from_settings(self.settings.players)
        self.console.write_line(WELCOME_TEXT)
        self._show(games[-1], names)

        while True:
            engine = games[-1]
            if engine.is_over:
                return engine.result
            try:
                typed = self.console.read_line(self._prompt(engine, names))
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
                self._show(engine, names)
                continue
            if command.command_type is CommandType.SHOW_HISTORY:
                self.console.write_line(
                    self.display.render_move_list(engine.turns) or NO_MOVES_YET_TEXT
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
                self._show(games[-1], names)
                continue
            if command.command_type is CommandType.RESIGN:
                games.append(engine.resign())
                self._show(games[-1], names)
                continue

            played = self._played(engine=engine, command_move_text=command.move_text)
            if played is None:
                continue
            games.append(played)
            self._show(played, names)

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

    def _show(self, engine: ChessEngine, names: PlayerNames) -> None:
        self.console.write_line("")
        self.console.write_line(self.display.render_board(engine.state))
        status = self.display.render_status(engine, names)
        if status:
            self.console.write_line(status)

    def _prompt(self, engine: ChessEngine, names: PlayerNames) -> str:
        # The console appends its own suffix; naming the player is this layer's job.
        name = names.get_name(engine.active_player)
        return f"{name} ({SIDE_NAMES_BY_COLOR[engine.state.side_to_move]}) "

    def _legal_moves_text(self, engine: ChessEngine) -> str:
        return MOVE_SEPARATOR.join(
            sorted(CoordinateNotation.to_text(move) for move in engine.legal_moves)
        )

    def _new_game(self) -> ChessEngine:
        return ChessEngine.new_game(
            white_participant=WHITE_PARTICIPANT, black_participant=BLACK_PARTICIPANT
        )
