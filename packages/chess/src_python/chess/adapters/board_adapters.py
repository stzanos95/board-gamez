"""
A position, between the schema's record of it and the board the engine
computes over.

The record lists the occupied squares; the board indexes them by square. Nothing
else differs, and nothing is converted but the shape.
"""

from idl.chess.model.board_pb2 import BoardState, SquareOccupant
from idl.chess.model.piece_pb2 import Occupant

from chess.board.chess_board_state import ChessBoardState
from chess.pieces.piece_factory import PieceFactory


class BoardAdapters:
    """
    A position, converted between the engine's board and the schema's record.
    """

    @staticmethod
    def state_to_message(state: ChessBoardState) -> BoardState:
        """
        Occupied squares are listed by square index, so one position always
        encodes to the same message.
        """
        return BoardState(
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
            halfmove_clock=state.halfmove_clock,
            fullmove_number=state.fullmove_number,
        )

    @staticmethod
    def message_to_state(message: BoardState) -> ChessBoardState:
        return ChessBoardState.from_pieces(
            pieces=(
                PieceFactory.create_piece(
                    piece_type=entry.occupant.piece_type,
                    color=entry.occupant.color,
                    square=entry.square,
                )
                for entry in message.occupancy
            ),
            side_to_move=message.side_to_move,
            castling_rights=message.castling_rights,
            en_passant_target=(
                message.en_passant_target if message.HasField("en_passant_target") else None
            ),
            halfmove_clock=message.halfmove_clock,
            fullmove_number=message.fullmove_number,
        )
