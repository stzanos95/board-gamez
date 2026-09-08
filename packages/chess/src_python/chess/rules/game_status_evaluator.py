from chess.board.chess_board_state import ChessBoardState
from chess.models.game_status import GameStatus
from chess.models.move import Move
from chess.models.position_key import PositionKey
from chess.rules.check_detector import CheckDetector
from chess.rules.fifty_move_rule import FiftyMoveRule
from chess.rules.insufficient_material_rule import InsufficientMaterialRule
from chess.rules.repetition_rule import RepetitionRule


class GameStatusEvaluator:
    @staticmethod
    def evaluate(
        state: ChessBoardState,
        position_keys: tuple[PositionKey, ...],
        legal_moves: tuple[Move, ...],
    ) -> GameStatus:
        """
        Read the position and report where the game stands.

        `legal_moves` are the moves available to the side to move, passed in
        because the caller has already built them and generating them is the most
        expensive step here.

        Having no legal move is decided first: a mate delivered on the hundredth
        quiet halfmove is a mate, not a draw by the fifty-move rule.
        """
        in_check = CheckDetector.is_in_check(state=state, color=state.side_to_move)
        if not legal_moves:
            return GameStatus.CHECKMATE if in_check else GameStatus.STALEMATE
        if InsufficientMaterialRule.is_draw(state):
            return GameStatus.DRAW_BY_INSUFFICIENT_MATERIAL
        if FiftyMoveRule.is_draw(state):
            return GameStatus.DRAW_BY_FIFTY_MOVE_RULE
        if RepetitionRule.is_draw(position_keys):
            return GameStatus.DRAW_BY_REPETITION
        return GameStatus.CHECK if in_check else GameStatus.IN_PROGRESS
