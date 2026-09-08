from enum import Enum


class MoveType(Enum):
    """
    What a move does beyond relocating its piece.

    Tells the board which further edits to make: removing a pawn from a square the
    mover does not land on, moving a rook alongside the king, or replacing the
    moved piece.
    """

    QUIET = "quiet"
    CAPTURE = "capture"
    DOUBLE_PAWN_PUSH = "double_pawn_push"
    EN_PASSANT = "en_passant"
    CASTLE = "castle"
    PROMOTION = "promotion"
    PROMOTION_CAPTURE = "promotion_capture"

    @property
    def is_capture(self) -> bool:
        return self in (MoveType.CAPTURE, MoveType.EN_PASSANT, MoveType.PROMOTION_CAPTURE)

    @property
    def is_promotion(self) -> bool:
        return self in (MoveType.PROMOTION, MoveType.PROMOTION_CAPTURE)
