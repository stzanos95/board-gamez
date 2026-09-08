from dataclasses import dataclass

from chess.contracts.board_state_view import BoardStateView
from chess.models.move import Move
from chess.models.piece_type import PieceType
from chess.models.square import Square
from chess.movement.direction_sets import ALL_EIGHT_DIRECTIONS
from chess.movement.ray_scanner import RayScanner
from chess.pieces.base_piece import BasePiece


@dataclass(frozen=True, slots=True)
class Queen(BasePiece):
    @property
    def piece_type(self) -> PieceType:
        return PieceType.QUEEN

    def pseudo_legal_moves(self, state: BoardStateView) -> tuple[Move, ...]:
        return RayScanner.moves_along_rays(
            state=state,
            origin=self.square,
            color=self.color,
            piece_type=self.piece_type,
            directions=ALL_EIGHT_DIRECTIONS,
        )

    def attacked_squares(self, state: BoardStateView) -> frozenset[Square]:
        return RayScanner.attacked_squares_along_rays(
            state=state, origin=self.square, directions=ALL_EIGHT_DIRECTIONS
        )
