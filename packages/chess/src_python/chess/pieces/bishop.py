from dataclasses import dataclass

from idl.chess.model.move_pb2 import Move
from idl.chess.model.piece_pb2 import PIECE_TYPE_BISHOP, PieceType

from chess.contracts.board_state_view import BoardStateView
from chess.core.squares import SquareIndex
from chess.movement.direction_sets import DIAGONAL_DIRECTIONS
from chess.movement.ray_scanner import RayScanner
from chess.pieces.base_piece import BasePiece


@dataclass(frozen=True, slots=True)
class Bishop(BasePiece):
    @property
    def piece_type(self) -> PieceType:
        return PIECE_TYPE_BISHOP

    def pseudo_legal_moves(self, state: BoardStateView) -> tuple[Move, ...]:
        return RayScanner.moves_along_rays(
            state=state,
            origin=self.square,
            color=self.color,
            piece_type=self.piece_type,
            directions=DIAGONAL_DIRECTIONS,
        )

    def attacked_squares(self, state: BoardStateView) -> frozenset[SquareIndex]:
        return RayScanner.attacked_squares_along_rays(
            state=state, origin=self.square, directions=DIAGONAL_DIRECTIONS
        )
