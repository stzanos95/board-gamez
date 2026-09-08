from dataclasses import dataclass

from chess.contracts.board_state_view import BoardStateView
from chess.models.move import Move
from chess.models.move_type import MoveType
from chess.models.piece_type import PieceType
from chess.models.square import Square
from chess.movement.step_scanner import StepScanner
from chess.pieces.base_piece import BasePiece
from chess.pieces.pawn_geometry import PAWN_PROMOTION_TYPES, PawnGeometry


@dataclass(frozen=True, slots=True)
class Pawn(BasePiece):
    """
    A pawn. Moves forward, captures diagonally, promotes on the last rank.

    Owns the double push, en passant and promotion. Each is decidable from the
    pawn's own square and one fact the board publishes, so none needs the rules
    layer.
    """

    @property
    def piece_type(self) -> PieceType:
        return PieceType.PAWN

    def pseudo_legal_moves(self, state: BoardStateView) -> tuple[Move, ...]:
        return self._push_moves(state) + self._capture_moves(state)

    def attacked_squares(self, state: BoardStateView) -> frozenset[Square]:
        # A pawn bears only on its two diagonals, never on the square ahead —
        # which is why a pawn cannot give check by advancing onto a king's file.
        return StepScanner.attacked_squares_at_offsets(
            origin=self.square,
            offsets=tuple(
                direction.vector for direction in PawnGeometry.capture_directions(self.color)
            ),
        )

    def _push_moves(self, state: BoardStateView) -> tuple[Move, ...]:
        forward = PawnGeometry.forward_direction(self.color).vector
        one_ahead = self.square.shifted(forward)
        if one_ahead is None or not state.is_empty(one_ahead):
            return ()

        found: list[Move] = list(self._advances_onto(one_ahead, capturing=False))

        if self.square.rank is not PawnGeometry.start_rank(self.color):
            return tuple(found)
        two_ahead = one_ahead.shifted(forward)
        if two_ahead is None or not state.is_empty(two_ahead):
            return tuple(found)
        found.append(
            Move(
                origin=self.square,
                destination=two_ahead,
                moving_color=self.color,
                moving_piece_type=self.piece_type,
                move_type=MoveType.DOUBLE_PAWN_PUSH,
            )
        )
        return tuple(found)

    def _capture_moves(self, state: BoardStateView) -> tuple[Move, ...]:
        found: list[Move] = []
        en_passant_target = state.en_passant_target_square()
        for direction in PawnGeometry.capture_directions(self.color):
            target = self.square.shifted(direction.vector)
            if target is None:
                continue
            if state.holds_enemy_of(target, self.color):
                found.extend(self._advances_onto(target, capturing=True))
            elif target == en_passant_target:
                # The pawn taken by en passant is beside us, not on the square we
                # land on — the only capture in chess that works this way.
                found.append(
                    Move(
                        origin=self.square,
                        destination=target,
                        moving_color=self.color,
                        moving_piece_type=self.piece_type,
                        move_type=MoveType.EN_PASSANT,
                        captured_square=Square(file=target.file, rank=self.square.rank),
                    )
                )
        return tuple(found)

    def _advances_onto(self, destination: Square, capturing: bool) -> tuple[Move, ...]:
        """
        One ordinary move, or the four a player chooses between on the last rank.
        """
        captured_square = destination if capturing else None
        if destination.rank is not PawnGeometry.promotion_rank(self.color):
            return (
                Move(
                    origin=self.square,
                    destination=destination,
                    moving_color=self.color,
                    moving_piece_type=self.piece_type,
                    move_type=MoveType.CAPTURE if capturing else MoveType.QUIET,
                    captured_square=captured_square,
                ),
            )
        move_type = MoveType.PROMOTION_CAPTURE if capturing else MoveType.PROMOTION
        return tuple(
            Move(
                origin=self.square,
                destination=destination,
                moving_color=self.color,
                moving_piece_type=self.piece_type,
                move_type=move_type,
                captured_square=captured_square,
                promotion_type=promotion_type,
            )
            for promotion_type in PAWN_PROMOTION_TYPES
        )
