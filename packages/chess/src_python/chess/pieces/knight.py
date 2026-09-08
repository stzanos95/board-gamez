from dataclasses import dataclass

from chess.contracts.board_state_view import BoardStateView
from chess.models.move import Move
from chess.models.piece_type import PieceType
from chess.models.square import Square
from chess.movement.knight_offsets import KNIGHT_OFFSETS
from chess.movement.step_scanner import StepScanner
from chess.pieces.base_piece import BasePiece


@dataclass(frozen=True, slots=True)
class Knight(BasePiece):
    @property
    def piece_type(self) -> PieceType:
        return PieceType.KNIGHT

    def pseudo_legal_moves(self, state: BoardStateView) -> tuple[Move, ...]:
        return StepScanner.moves_to_offsets(
            state=state,
            origin=self.square,
            color=self.color,
            piece_type=self.piece_type,
            offsets=KNIGHT_OFFSETS,
        )

    def attacked_squares(self, state: BoardStateView) -> frozenset[Square]:
        return StepScanner.attacked_squares_at_offsets(origin=self.square, offsets=KNIGHT_OFFSETS)
