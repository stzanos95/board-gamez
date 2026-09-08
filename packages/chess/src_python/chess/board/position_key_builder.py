"""
Summarising a board state as a comparable key.

Separate from PositionKey so that models carry no dependency on a board.
"""

from chess.board.chess_board_state import ChessBoardState
from chess.models.occupant import Occupant
from chess.models.position_key import PositionKey
from chess.models.square_occupant import SquareOccupant


class PositionKeyBuilder:
    """
    Reading a board state into the key the repetition rule compares.
    """

    @staticmethod
    def build_key_from_state(state: ChessBoardState) -> PositionKey:
        """
        The comparable key for this state.

        Drops both clocks, which differ between repetitions of the same position
        and so must not take part in the comparison.
        """
        return PositionKey(
            occupancy=frozenset(
                SquareOccupant(
                    square=piece.square,
                    occupant=Occupant(color=piece.color, piece_type=piece.piece_type),
                )
                for piece in state.pieces.values()
            ),
            side_to_move=state.side_to_move,
            castling_rights=state.castling_rights,
            en_passant_target=state.en_passant_target,
        )
