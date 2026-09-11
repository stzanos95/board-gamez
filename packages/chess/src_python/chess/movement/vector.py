from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Vector:
    """
    A displacement across the board, in files and ranks.

    Rank deltas run from White's point of view: a positive delta moves towards
    rank 8.
    """

    file_delta: int
    rank_delta: int

    def scaled(self, factor: int) -> "Vector":
        return Vector(file_delta=self.file_delta * factor, rank_delta=self.rank_delta * factor)

    @property
    def reversed(self) -> "Vector":
        return Vector(file_delta=-self.file_delta, rank_delta=-self.rank_delta)
