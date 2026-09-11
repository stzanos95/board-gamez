from dataclasses import dataclass

from idl.chess.model.move_pb2 import Move
from idl.chess.model.piece_pb2 import PIECE_TYPE_KNIGHT, PieceType

from chess.contracts.board_state_view import BoardStateView
from chess.core.squares import SquareIndex
from chess.movement.knight_offsets import KNIGHT_OFFSETS
from chess.movement.step_scanner import StepScanner
from chess.pieces.base_piece import BasePiece


@dataclass(frozen=True, slots=True)
class Knight(BasePiece):
    @property
    def piece_type(self) -> PieceType:
        return PIECE_TYPE_KNIGHT

    def pseudo_legal_moves(self, state: BoardStateView) -> tuple[Move, ...]:
        return StepScanner.moves_to_offsets(
            state=state,
            origin=self.square,
            color=self.color,
            piece_type=self.piece_type,
            offsets=KNIGHT_OFFSETS,
        )

    def attacked_squares(self, state: BoardStateView) -> frozenset[SquareIndex]:
        return StepScanner.attacked_squares_at_offsets(origin=self.square, offsets=KNIGHT_OFFSETS)
