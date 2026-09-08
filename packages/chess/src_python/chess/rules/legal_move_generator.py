"""
Turning what the pieces offer into what the rules permit.

Pieces contribute everything their geometry allows, knowing nothing about kings.
This adds castling and discards every candidate that would leave its own king in
check.

Legality is tested by playing the move and reading the result. Pins, discovered
checks and a king retreating along a checking ray need no special case.
"""

from chess.board.chess_board_state import ChessBoardState
from chess.models.color import Color
from chess.models.move import Move
from chess.rules.castling_rule import CastlingRule
from chess.rules.check_detector import CheckDetector


class LegalMoveGenerator:
    @staticmethod
    def moves_for(state: ChessBoardState, color: Color) -> tuple[Move, ...]:
        candidates: list[Move] = []
        for piece in state.pieces_of(color):
            candidates.extend(piece.pseudo_legal_moves(state))
        candidates.extend(CastlingRule.moves_for(state=state, color=color))
        return tuple(
            move for move in candidates if LegalMoveGenerator.leaves_own_king_safe(state, move)
        )

    @staticmethod
    def moves_for_side_to_move(state: ChessBoardState) -> tuple[Move, ...]:
        return LegalMoveGenerator.moves_for(state=state, color=state.side_to_move)

    @staticmethod
    def leaves_own_king_safe(state: ChessBoardState, move: Move) -> bool:
        return not CheckDetector.is_in_check(state.apply(move), move.moving_color)
