from dataclasses import dataclass, replace

from idl.chess.model.board_pb2 import PositionKey
from idl.chess.model.game_pb2 import (
    GAME_OUTCOME_BLACK_WINS,
    GAME_OUTCOME_DRAW,
    GAME_OUTCOME_WHITE_WINS,
    GAME_STATUS_CHECKMATE,
    ChessPlayer,
    ChessTurn,
    GameOutcome,
    GameResult,
    GameStatus,
    PlayerRoster,
)
from idl.chess.model.move_pb2 import Move
from idl.chess.model.piece_pb2 import COLOR_BLACK, COLOR_WHITE, Color

from chess.board.chess_board_state import ChessBoardState
from chess.board.position_key_builder import PositionKeyBuilder
from chess.board.starting_position import StartingPosition
from chess.core.colors import Colors
from chess.core.errors import IllegalMoveError
from chess.core.game_statuses import GameStatuses
from chess.engine.roster_lookup import RosterLookup
from chess.notation.coordinate_notation import CoordinateNotation
from chess.notation.standard_algebraic_notation import StandardAlgebraicNotation
from chess.rules.game_status_evaluator import GameStatusEvaluator
from chess.rules.legal_move_generator import LegalMoveGenerator

OutcomesByWinningColor = dict[Color, GameOutcome]

OUTCOMES_BY_WINNING_COLOR: OutcomesByWinningColor = {
    COLOR_WHITE: GAME_OUTCOME_WHITE_WINS,
    COLOR_BLACK: GAME_OUTCOME_BLACK_WINS,
}


@dataclass(frozen=True, slots=True)
class ChessEngine:
    """
    A game in progress: the players, the position, and the moves played.

    Immutable. `play` returns the next game, so an earlier engine remains a
    playable game and taking a move back means keeping it. The messages it holds
    are never edited after construction.

    `position_keys` runs one ahead of `turns`: the opening position counts as
    visited before either player has moved.

    `legal_moves` and `status` are fields rather than properties. Both are
    expensive and both are read several times per move, so they are computed once
    at construction.
    """

    roster: PlayerRoster
    state: ChessBoardState
    turns: tuple[ChessTurn, ...]
    position_keys: tuple[PositionKey, ...]
    legal_moves: tuple[Move, ...]
    status: GameStatus
    resigning_color: Color | None

    @staticmethod
    def new_game(white_participant: int, black_participant: int) -> "ChessEngine":
        state = StartingPosition.build_state()
        legal_moves = LegalMoveGenerator.moves_for_side_to_move(state)
        opening_key = PositionKeyBuilder.build_key_from_state(state)
        return ChessEngine(
            roster=PlayerRoster(
                white=ChessPlayer(color=COLOR_WHITE, participant=white_participant),
                black=ChessPlayer(color=COLOR_BLACK, participant=black_participant),
            ),
            state=state,
            turns=(),
            position_keys=(opening_key,),
            legal_moves=legal_moves,
            status=GameStatusEvaluator.evaluate(
                state=state, position_keys=(opening_key,), legal_moves=legal_moves
            ),
            resigning_color=None,
        )

    @property
    def active_player(self) -> ChessPlayer:
        return RosterLookup.get_player(self.roster, self.state.side_to_move)

    @property
    def is_over(self) -> bool:
        return self.resigning_color is not None or GameStatuses.is_terminal(self.status)

    def play(self, move: Move) -> "ChessEngine":
        """
        The game as it stands after this move, which must be one of the legal ones.
        """
        if self.is_over:
            raise IllegalMoveError(
                f"the game is over ({GameStatus.Name(self.status)}); "
                f"{CoordinateNotation.to_text(move)} cannot be played"
            )
        if move not in self.legal_moves:
            available = sorted(CoordinateNotation.to_text(legal) for legal in self.legal_moves)
            raise IllegalMoveError(
                f"{CoordinateNotation.to_text(move)} is not legal for "
                f"{Color.Name(self.state.side_to_move)}; the legal moves are "
                f"{', '.join(available)}"
            )

        next_board = self.state.apply(move)
        next_legal_moves = LegalMoveGenerator.moves_for_side_to_move(next_board)
        next_key = PositionKeyBuilder.build_key_from_state(next_board)
        next_position_keys = (*self.position_keys, next_key)
        next_status = GameStatusEvaluator.evaluate(
            state=next_board,
            position_keys=next_position_keys,
            legal_moves=next_legal_moves,
        )
        turn = ChessTurn(
            number=self.state.fullmove_number,
            player=self.active_player,
            move=move,
            # Named against the position it was played from, which is this one.
            notation=StandardAlgebraicNotation.to_text(
                move=move, legal_moves=self.legal_moves, resulting_status=next_status
            ),
            resulting_status=next_status,
        )
        return ChessEngine(
            roster=self.roster,
            state=next_board,
            turns=(*self.turns, turn),
            position_keys=next_position_keys,
            legal_moves=next_legal_moves,
            status=next_status,
            resigning_color=None,
        )

    def resign(self, color: Color) -> "ChessEngine":
        """
        The game as it stands after this side gives up, whether or not it is
        their move.
        """
        if self.is_over:
            raise IllegalMoveError(f"the game is already over ({GameStatus.Name(self.status)})")
        return replace(self, resigning_color=color)

    @property
    def result(self) -> GameResult | None:
        """
        How the game finished, or None while it is still being played.
        """
        if self.resigning_color is not None:
            winner_color = Colors.opponent(self.resigning_color)
            return GameResult(
                outcome=OUTCOMES_BY_WINNING_COLOR[winner_color],
                winner=RosterLookup.get_player(self.roster, winner_color),
                resigning_player=RosterLookup.get_player(self.roster, self.resigning_color),
            )
        if not GameStatuses.is_terminal(self.status):
            return None
        if self.status == GAME_STATUS_CHECKMATE:
            # The side to move is the side with no escape, so the other one won.
            winner_color = Colors.opponent(self.state.side_to_move)
            return GameResult(
                outcome=OUTCOMES_BY_WINNING_COLOR[winner_color],
                winner=RosterLookup.get_player(self.roster, winner_color),
                status=self.status,
            )
        return GameResult(outcome=GAME_OUTCOME_DRAW, status=self.status)
