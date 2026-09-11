"""
Summarising a board state as a comparable key.
"""

from idl.chess.model.board_pb2 import PositionKey, SquareOccupant
from idl.chess.model.piece_pb2 import Occupant

from chess.board.chess_board_state import ChessBoardState


class PositionKeyBuilder:
    """
    Reading a board state into the key the repetition rule compares.
    """

    @staticmethod
    def build_key_from_state(state: ChessBoardState) -> PositionKey:
        """
        The comparable key for this state.

        Drops both clocks, which differ between repetitions of the same position
        and so must not take part in the comparison. The occupancy is listed by
        square index, so two keys of one position are equal messages.
        """
        return PositionKey(
            occupancy=[
                SquareOccupant(
                    square=piece.square,
                    occupant=Occupant(color=piece.color, piece_type=piece.piece_type),
                )
                for _, piece in sorted(state.pieces.items())
            ],
            side_to_move=state.side_to_move,
            castling_rights=state.castling_rights,
            en_passant_target=state.en_passant_target,
        )
