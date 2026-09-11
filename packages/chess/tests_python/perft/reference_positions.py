"""
The standard perft positions.

Perft counts every distinct sequence of legal moves to a given depth. The expected
totals are published, so a wrong count points at a rule rather than a symptom.

These four reference positions exercise castling, en passant, promotion, pins and
check evasion. The opening position reaches none of those at a workable depth.
"""

from dataclasses import dataclass

from idl.chess.model.piece_pb2 import COLOR_WHITE, Color


@dataclass(frozen=True, slots=True)
class PerftPosition:
    """
    A position and the node counts it must produce at each depth.
    """

    name: str
    placement: str
    side_to_move: Color
    castling_text: str
    en_passant_target: str | None
    node_counts: dict[int, int]
    slow_from_depth: int


OPENING = PerftPosition(
    name="opening position",
    placement="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
    side_to_move=COLOR_WHITE,
    castling_text="KQkq",
    en_passant_target=None,
    node_counts={1: 20, 2: 400, 3: 8902, 4: 197281},
    slow_from_depth=4,
)

CASTLING_HEAVY = PerftPosition(
    name="castling and pins",
    placement="r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R",
    side_to_move=COLOR_WHITE,
    castling_text="KQkq",
    en_passant_target=None,
    node_counts={1: 48, 2: 2039, 3: 97862},
    slow_from_depth=3,
)

EN_PASSANT_HEAVY = PerftPosition(
    name="en passant and promotion race",
    placement="8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8",
    side_to_move=COLOR_WHITE,
    castling_text="",
    en_passant_target=None,
    node_counts={1: 14, 2: 191, 3: 2812, 4: 43238},
    slow_from_depth=5,
)

PROMOTION_HEAVY = PerftPosition(
    name="promotions",
    placement="r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1",
    side_to_move=COLOR_WHITE,
    castling_text="kq",
    en_passant_target=None,
    node_counts={1: 6, 2: 264, 3: 9467},
    slow_from_depth=4,
)

REFERENCE_POSITIONS: tuple[PerftPosition, ...] = (
    OPENING,
    CASTLING_HEAVY,
    EN_PASSANT_HEAVY,
    PROMOTION_HEAVY,
)
