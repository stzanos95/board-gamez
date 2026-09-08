from enum import Enum


class Color(Enum):
    """
    Which side a piece belongs to.
    """

    WHITE = "white"
    BLACK = "black"

    @property
    def opponent(self) -> "Color":
        return Color.BLACK if self is Color.WHITE else Color.WHITE
