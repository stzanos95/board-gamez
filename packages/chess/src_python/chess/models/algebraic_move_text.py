from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AlgebraicMoveText:
    """
    A move as a scoresheet writes it: "Nf3", "exd5", "O-O", "e8=Q#".

    A named type rather than a bare string, because coordinate text ("g1f3") is
    also a string and the two are not interchangeable.
    """

    text: str
