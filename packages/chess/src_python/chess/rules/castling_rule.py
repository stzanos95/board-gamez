"""
Generating castles.

Castling belongs to the rules layer rather than to the king because the king may
not pass through a square the enemy attacks, and answering that needs every enemy
piece on the board.
"""

from chess.board.chess_board_state import ChessBoardState
from chess.models.castling_geometry import CastlingGeometry, CastlingGeometryLookup
from chess.models.color import Color
from chess.models.move import Move
from chess.models.move_type import MoveType
from chess.models.piece_type import PieceType
from chess.models.square import Square
from chess.rules.attack_map import AttackMap


class CastlingRule:
    @staticmethod
    def moves_for(state: ChessBoardState, color: Color) -> tuple[Move, ...]:
        return tuple(
            CastlingRule._move_from(geometry=geometry, color=color)
            for geometry in CastlingGeometryLookup.geometries_for_color(color)
            if CastlingRule._is_available(state=state, geometry=geometry, color=color)
        )

    @staticmethod
    def _is_available(state: ChessBoardState, geometry: CastlingGeometry, color: Color) -> bool:
        if not state.available_castling_rights().allows(color, geometry.right.side):
            return False
        if not CastlingRule._stands_on(state, geometry.king_origin, color, PieceType.KING):
            return False
        if not CastlingRule._stands_on(state, geometry.rook_origin, color, PieceType.ROOK):
            return False
        if any(not state.is_empty(square) for square in geometry.vacant_squares):
            return False
        # Out of check, through check and into check are all forbidden, which is
        # why this checks the king's origin as well as its path.
        return not any(
            AttackMap.is_square_attacked_by(state=state, square=square, color=color.opponent)
            for square in geometry.unattacked_squares
        )

    @staticmethod
    def _stands_on(
        state: ChessBoardState, square: Square, color: Color, piece_type: PieceType
    ) -> bool:
        piece = state.piece_at(square)
        return piece is not None and piece.color is color and piece.piece_type is piece_type

    @staticmethod
    def _move_from(geometry: CastlingGeometry, color: Color) -> Move:
        return Move(
            origin=geometry.king_origin,
            destination=geometry.king_destination,
            moving_color=color,
            moving_piece_type=PieceType.KING,
            move_type=MoveType.CASTLE,
            castling_side=geometry.right.side,
            rook_origin=geometry.rook_origin,
            rook_destination=geometry.rook_destination,
        )
