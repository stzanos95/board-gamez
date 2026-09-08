from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from chess.contracts.board_state_view import BoardStateView
from chess.core.errors import BoardStateError
from chess.models.castling_geometry import CastlingGeometryLookup
from chess.models.castling_rights import CastlingRights
from chess.models.color import Color
from chess.models.move import Move
from chess.models.move_type import MoveType
from chess.models.occupant import Occupant
from chess.models.piece_type import PieceType
from chess.models.square import Square
from chess.pieces.base_piece import BasePiece
from chess.pieces.pawn_geometry import PawnGeometry
from chess.pieces.piece_factory import PieceFactory

STARTING_HALFMOVE_CLOCK = 0
STARTING_FULLMOVE_NUMBER = 1
CLOCK_INCREMENT = 1


@dataclass(frozen=True, slots=True)
class ChessBoardState(BoardStateView):
    """
    A complete position: pieces, side to move, castling rights, en-passant
    target and both clocks.

    Immutable. `apply` returns a new board and is the only producer of board
    state, so the six fields stay consistent with each other.

    `pieces` maps each occupied square to the piece standing on it. It is a
    read-only view: the state owns it and nothing can write through it.
    """

    pieces: Mapping[Square, BasePiece]
    side_to_move: Color
    castling_rights: CastlingRights
    en_passant_target: Square | None
    halfmove_clock: int
    fullmove_number: int

    # --- BoardStateView: what a piece is allowed to see -------------------------

    def occupant(self, square: Square) -> Occupant | None:
        piece = self.pieces.get(square)
        if piece is None:
            return None
        return Occupant(color=piece.color, piece_type=piece.piece_type)

    def is_empty(self, square: Square) -> bool:
        return square not in self.pieces

    def holds_enemy_of(self, square: Square, color: Color) -> bool:
        piece = self.pieces.get(square)
        return piece is not None and piece.color is not color

    def holds_ally_of(self, square: Square, color: Color) -> bool:
        piece = self.pieces.get(square)
        return piece is not None and piece.color is color

    def en_passant_target_square(self) -> Square | None:
        return self.en_passant_target

    def available_castling_rights(self) -> CastlingRights:
        return self.castling_rights

    # --- what the rules layer needs, which is more than a piece gets -------

    def piece_at(self, square: Square) -> BasePiece | None:
        return self.pieces.get(square)

    def pieces_of(self, color: Color) -> tuple[BasePiece, ...]:
        return tuple(piece for piece in self.pieces.values() if piece.color is color)

    def king_square(self, color: Color) -> Square | None:
        """
        Where this side's king stands, or None if the position has no king.

        Returns None rather than raising, so a test may build a position holding
        a single piece.
        """
        for piece in self.pieces.values():
            if piece.color is color and piece.piece_type is PieceType.KING:
                return piece.square
        return None

    # --- the single writer -------------------------------------------------

    def apply(self, move: Move) -> "ChessBoardState":
        """
        The position that results from playing this move.

        The move is applied as given. Deciding whether it is legal belongs to the
        rules layer.
        """
        mover = self.pieces.get(move.origin)
        if mover is None:
            raise BoardStateError(f"no piece stands on {move.origin.algebraic} to play {move}")

        remaining = dict(self.pieces)
        if move.captured_square is not None:
            # Not always the destination: en passant takes a pawn standing beside
            # the square the capturing pawn lands on.
            remaining.pop(move.captured_square, None)
        del remaining[move.origin]

        if move.promotion_type is None:
            remaining[move.destination] = mover.relocated_to(move.destination)
        else:
            remaining[move.destination] = PieceFactory.create_piece(
                piece_type=move.promotion_type, color=mover.color, square=move.destination
            )

        if move.rook_origin is not None and move.rook_destination is not None:
            rook = remaining.pop(move.rook_origin, None)
            if rook is None:
                raise BoardStateError(
                    f"castling from {move.origin.algebraic} found no rook on "
                    f"{move.rook_origin.algebraic}"
                )
            remaining[move.rook_destination] = rook.relocated_to(move.rook_destination)

        return ChessBoardState(
            pieces=MappingProxyType(remaining),
            side_to_move=self.side_to_move.opponent,
            castling_rights=self._rights_after(move),
            en_passant_target=self._en_passant_target_after(move),
            halfmove_clock=self._halfmove_clock_after(move),
            fullmove_number=self._fullmove_number_after(),
        )

    def _rights_after(self, move: Move) -> CastlingRights:
        rights = self.castling_rights
        if move.moving_piece_type is PieceType.KING:
            # A king that moves at all — castling included — gives up both castles.
            rights = rights.without_color(move.moving_color)
        vacated = CastlingGeometryLookup.right_anchored_at_square(move.origin)
        if vacated is not None and move.moving_piece_type is PieceType.ROOK:
            rights = rights.without(vacated)
        if move.captured_square is not None:
            # Capturing a rook on its home square kills that castle just as surely
            # as moving it would have.
            taken = CastlingGeometryLookup.right_anchored_at_square(move.captured_square)
            if taken is not None:
                rights = rights.without(taken)
        return rights

    def _en_passant_target_after(self, move: Move) -> Square | None:
        if move.move_type is not MoveType.DOUBLE_PAWN_PUSH:
            return None
        return move.origin.shifted(PawnGeometry.forward_direction(move.moving_color).vector)

    def _halfmove_clock_after(self, move: Move) -> int:
        if move.moving_piece_type is PieceType.PAWN or move.move_type.is_capture:
            return STARTING_HALFMOVE_CLOCK
        return self.halfmove_clock + CLOCK_INCREMENT

    def _fullmove_number_after(self) -> int:
        if self.side_to_move is Color.BLACK:
            return self.fullmove_number + CLOCK_INCREMENT
        return self.fullmove_number

    # --- construction ------------------------------------------------------

    @staticmethod
    def from_pieces(
        pieces: Iterable[BasePiece],
        side_to_move: Color = Color.WHITE,
        castling_rights: CastlingRights | None = None,
        en_passant_target: Square | None = None,
        halfmove_clock: int = STARTING_HALFMOVE_CLOCK,
        fullmove_number: int = STARTING_FULLMOVE_NUMBER,
    ) -> "ChessBoardState":
        """
        Build a position from loose pieces.

        Castling rights default to none. A hand-built position rarely has the
        king and both rooks untouched on their home squares.
        """
        return ChessBoardState(
            pieces=MappingProxyType({piece.square: piece for piece in pieces}),
            side_to_move=side_to_move,
            castling_rights=CastlingRights.none() if castling_rights is None else castling_rights,
            en_passant_target=en_passant_target,
            halfmove_clock=halfmove_clock,
            fullmove_number=fullmove_number,
        )
