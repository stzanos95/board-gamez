"""
Generating castles.

Castling belongs to the rules layer rather than to the king because the king may
not pass through a square the enemy attacks, and answering that needs every enemy
piece on the board.
"""

from idl.chess.model.move_pb2 import MOVE_TYPE_CASTLE, Move
from idl.chess.model.piece_pb2 import PIECE_TYPE_KING, PIECE_TYPE_ROOK, Color, PieceType
from idl.chess.model.square_pb2 import Square

from chess.board.chess_board_state import ChessBoardState
from chess.core.castling_rights import CastlingRightSets
from chess.core.colors import Colors
from chess.rules.attack_map import AttackMap
from chess.rules.castling_geometry import CastlingGeometry, CastlingGeometryLookup


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
        if not CastlingRightSets.allows(
            state.available_castling_rights(), color, geometry.right.side
        ):
            return False
        if not CastlingRule._stands_on(state, geometry.king_origin, color, PIECE_TYPE_KING):
            return False
        if not CastlingRule._stands_on(state, geometry.rook_origin, color, PIECE_TYPE_ROOK):
            return False
        if any(not state.is_empty(square) for square in geometry.vacant_squares):
            return False
        # Out of check, through check and into check are all forbidden, which is
        # why this checks the king's origin as well as its path.
        return not any(
            AttackMap.is_square_attacked_by(
                state=state, square=square, color=Colors.opponent(color)
            )
            for square in geometry.unattacked_squares
        )

    @staticmethod
    def _stands_on(
        state: ChessBoardState, square: Square, color: Color, piece_type: PieceType
    ) -> bool:
        piece = state.piece_at(square)
        return piece is not None and piece.color == color and piece.piece_type == piece_type

    @staticmethod
    def _move_from(geometry: CastlingGeometry, color: Color) -> Move:
        return Move(
            origin=geometry.king_origin,
            destination=geometry.king_destination,
            moving_color=color,
            moving_piece_type=PIECE_TYPE_KING,
            move_type=MOVE_TYPE_CASTLE,
            castling_side=geometry.right.side,
            rook_origin=geometry.rook_origin,
            rook_destination=geometry.rook_destination,
        )
