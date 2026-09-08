from enum import Enum


class CastlingSide(Enum):
    """
    Which rook a castle uses.
    """

    KINGSIDE = "kingside"
    QUEENSIDE = "queenside"
