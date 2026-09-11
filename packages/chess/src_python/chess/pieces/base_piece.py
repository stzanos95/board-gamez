from abc import ABC, abstractmethod
from dataclasses import dataclass, replace

from idl.chess.model.move_pb2 import Move
from idl.chess.model.piece_pb2 import Color, PieceType
from idl.chess.model.square_pb2 import Square

from chess.contracts.board_state_view import BoardStateView
from chess.core.squares import SquareIndex


@dataclass(frozen=True, slots=True)
class BasePiece(ABC):
    """
    A single chessman: a colour, a square, and the geometry of how it travels.

    A piece reads a position and never changes one. It is handed a BoardStateView
    rather than the board.

    It offers two generators because they differ: a pawn moves forward and attacks
    diagonally, and a king bears on squares it may not legally enter. Check
    detection uses the attack generator, and answers square indexes so the set
    can be built and searched.

    A piece does not decide legality. Anything needing the whole board belongs to
    the rules layer.
    """

    color: Color
    square: Square

    @property
    @abstractmethod
    def piece_type(self) -> PieceType: ...

    @abstractmethod
    def pseudo_legal_moves(self, state: BoardStateView) -> tuple[Move, ...]:
        """
        Every move this piece's geometry allows, ignoring king safety.
        """

    @abstractmethod
    def attacked_squares(self, state: BoardStateView) -> frozenset[SquareIndex]:
        """
        Every square this piece bears on, including ones it defends.
        """

    def relocated_to(self, square: Square) -> "BasePiece":
        """
        The same piece, standing on another square.

        Returns a new piece. The one passed in is unchanged.
        """
        return replace(self, square=square)
