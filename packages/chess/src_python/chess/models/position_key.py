from dataclasses import dataclass

from chess.models.castling_rights import CastlingRights
from chess.models.color import Color
from chess.models.square import Square
from chess.models.square_occupant import SquareOccupant


@dataclass(frozen=True, slots=True)
class PositionKey:
    """
    What makes two positions the same for the repetition rule: the same pieces
    on the same squares, the same side to move, the same castling rights and the
    same en-passant square.

    Building one from a board lives in `board.position_key_builder`.

    The laws compare whether an en-passant capture is available; this compares the
    target square. A repetition draw is therefore sometimes recognised one move
    later than the laws allow, never earlier.
    """

    occupancy: frozenset[SquareOccupant]
    side_to_move: Color
    castling_rights: CastlingRights
    en_passant_target: Square | None
