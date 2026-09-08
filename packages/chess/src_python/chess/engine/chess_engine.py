from dataclasses import dataclass, replace

from chess.board.chess_board_state import ChessBoardState
from chess.board.position_key_builder import PositionKeyBuilder
from chess.board.starting_position import StartingPosition
from chess.core.errors import IllegalMoveError
from chess.models.chess_player import ChessPlayer
from chess.models.chess_turn import ChessTurn
from chess.models.chess_turn_history import ChessTurnHistory
from chess.models.color import Color
from chess.models.game_outcome import GameOutcome
from chess.models.game_result import GameResult
from chess.models.game_status import GameStatus
from chess.models.move import Move
from chess.models.player_roster import PlayerRoster
from chess.notation.coordinate_notation import CoordinateNotation
from chess.notation.standard_algebraic_notation import StandardAlgebraicNotation
from chess.rules.game_status_evaluator import GameStatusEvaluator
from chess.rules.legal_move_generator import LegalMoveGenerator


@dataclass(frozen=True, slots=True)
class ChessEngine:
    """
    A game in progress: the players, the position, and the moves played.

    Immutable. `play` returns the next game, so an earlier engine remains a
    playable game and taking a move back means keeping it.

    `legal_moves` and `status` are fields rather than properties. Both are
    expensive and both are read several times per move, so they are computed once
    at construction.
    """

    roster: PlayerRoster
    state: ChessBoardState
    history: ChessTurnHistory
    legal_moves: tuple[Move, ...]
    status: GameStatus
    resigning_color: Color | None

    @staticmethod
    def new_game(white: ChessPlayer, black: ChessPlayer) -> "ChessEngine":
        state = StartingPosition.build_state()
        legal_moves = LegalMoveGenerator.moves_for_side_to_move(state)
        opening_key = PositionKeyBuilder.build_key_from_state(state)
        return ChessEngine(
            roster=PlayerRoster(white=white, black=black),
            state=state,
            history=ChessTurnHistory.opening(initial_position_key=opening_key),
            legal_moves=legal_moves,
            status=GameStatusEvaluator.evaluate(
                state=state, position_keys=(opening_key,), legal_moves=legal_moves
            ),
            resigning_color=None,
        )

    @property
    def active_player(self) -> ChessPlayer:
        return self.roster.player_for(self.state.side_to_move)

    @property
    def is_over(self) -> bool:
        return self.resigning_color is not None or self.status.is_terminal

    def play(self, move: Move) -> "ChessEngine":
        """
        The game as it stands after this move, which must be one of the legal ones.
        """
        if self.is_over:
            raise IllegalMoveError(
                f"the game is over ({self.status.value}); {CoordinateNotation.to_text(move)} "
                f"cannot be played"
            )
        if move not in self.legal_moves:
            available = sorted(CoordinateNotation.to_text(legal) for legal in self.legal_moves)
            raise IllegalMoveError(
                f"{CoordinateNotation.to_text(move)} is not legal for "
                f"{self.active_player.name}; the legal moves are {', '.join(available)}"
            )

        next_board = self.state.apply(move)
        next_legal_moves = LegalMoveGenerator.moves_for_side_to_move(next_board)
        next_key = PositionKeyBuilder.build_key_from_state(next_board)
        next_status = GameStatusEvaluator.evaluate(
            state=next_board,
            position_keys=(*self.history.position_keys, next_key),
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
            history=self.history.extended(turn=turn, position_key=next_key),
            legal_moves=next_legal_moves,
            status=next_status,
            resigning_color=None,
        )

    def resign(self) -> "ChessEngine":
        """
        The game as it stands after the player to move gives up.
        """
        if self.is_over:
            raise IllegalMoveError(f"the game is already over ({self.status.value})")
        return replace(self, resigning_color=self.state.side_to_move)

    @property
    def result(self) -> GameResult | None:
        """
        How the game finished, or None while it is still being played.
        """
        if self.resigning_color is not None:
            return GameResult(
                outcome=GameOutcome.for_winner(self.resigning_color.opponent),
                winner=self.roster.player_for(self.resigning_color.opponent),
                status=None,
                resigning_player=self.roster.player_for(self.resigning_color),
            )
        if not self.status.is_terminal:
            return None
        if self.status is GameStatus.CHECKMATE:
            # The side to move is the side with no escape, so the other one won.
            winner_color = self.state.side_to_move.opponent
            return GameResult(
                outcome=GameOutcome.for_winner(winner_color),
                winner=self.roster.player_for(winner_color),
                status=self.status,
                resigning_player=None,
            )
        return GameResult(
            outcome=GameOutcome.DRAW, winner=None, status=self.status, resigning_player=None
        )
