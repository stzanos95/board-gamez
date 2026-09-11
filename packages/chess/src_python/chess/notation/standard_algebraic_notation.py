"""
Moves written as a scoresheet writes them: "Nf3", "exd5", "O-O", "e8=Q#".

Rendering needs the position's legal moves. A move's name depends on what the
other pieces could have done: "Nf3" becomes "Ngf3" when a second knight also
reaches f3.
"""

from idl.chess.model.castling_pb2 import CASTLING_SIDE_QUEENSIDE
from idl.chess.model.game_pb2 import GAME_STATUS_CHECK, GAME_STATUS_CHECKMATE, GameStatus
from idl.chess.model.move_pb2 import MOVE_TYPE_CASTLE, Move
from idl.chess.model.piece_pb2 import PIECE_TYPE_PAWN, PIECE_TYPE_UNSPECIFIED

from chess.core.files import Files
from chess.core.move_types import MoveTypes
from chess.core.ranks import Ranks
from chess.core.squares import Squares
from chess.notation.piece_letters import PieceLetters

KINGSIDE_CASTLE_TEXT = "O-O"
QUEENSIDE_CASTLE_TEXT = "O-O-O"
CAPTURE_MARK = "x"
PROMOTION_MARK = "="
CHECK_MARK = "+"
CHECKMATE_MARK = "#"


class StandardAlgebraicNotation:
    """
    Writing a move the way a scoresheet does.
    """

    @staticmethod
    def to_text(move: Move, legal_moves: tuple[Move, ...], resulting_status: GameStatus) -> str:
        """
        Render a move about to be played from the given position.

        `legal_moves` are the moves available before the move is played.
        `resulting_status` describes the position it leads to.
        """
        suffix = StandardAlgebraicNotation._suffix(resulting_status)
        if move.move_type == MOVE_TYPE_CASTLE:
            return StandardAlgebraicNotation._castle_text(move) + suffix
        body = (
            StandardAlgebraicNotation._pawn_body(move)
            if move.moving_piece_type == PIECE_TYPE_PAWN
            else StandardAlgebraicNotation._piece_body(move, legal_moves)
        )
        return body + StandardAlgebraicNotation._promotion_text(move) + suffix

    @staticmethod
    def _castle_text(move: Move) -> str:
        if move.castling_side == CASTLING_SIDE_QUEENSIDE:
            return QUEENSIDE_CASTLE_TEXT
        return KINGSIDE_CASTLE_TEXT

    @staticmethod
    def _pawn_body(move: Move) -> str:
        if not MoveTypes.is_capture(move.move_type):
            return Squares.algebraic(move.destination)
        # A capturing pawn is always named by the file it left, even when only one
        # pawn could have made the capture.
        return (
            f"{Files.letter(move.origin.file)}{CAPTURE_MARK}{Squares.algebraic(move.destination)}"
        )

    @staticmethod
    def _piece_body(move: Move, legal_moves: tuple[Move, ...]) -> str:
        letter = PieceLetters.notation_letter(move.moving_piece_type)
        capture = CAPTURE_MARK if MoveTypes.is_capture(move.move_type) else ""
        disambiguation = StandardAlgebraicNotation._disambiguation(move, legal_moves)
        return f"{letter}{disambiguation}{capture}{Squares.algebraic(move.destination)}"

    @staticmethod
    def _disambiguation(move: Move, legal_moves: tuple[Move, ...]) -> str:
        rivals = tuple(
            other
            for other in legal_moves
            if other.moving_piece_type == move.moving_piece_type
            and other.moving_color == move.moving_color
            and other.destination == move.destination
            and other.origin != move.origin
        )
        if not rivals:
            return ""
        if all(rival.origin.file != move.origin.file for rival in rivals):
            return Files.letter(move.origin.file)
        if all(rival.origin.rank != move.origin.rank for rival in rivals):
            return Ranks.digit(move.origin.rank)
        return Squares.algebraic(move.origin)

    @staticmethod
    def _promotion_text(move: Move) -> str:
        if move.promotion_type == PIECE_TYPE_UNSPECIFIED:
            return ""
        return f"{PROMOTION_MARK}{PieceLetters.notation_letter(move.promotion_type)}"

    @staticmethod
    def _suffix(resulting_status: GameStatus) -> str:
        if resulting_status == GAME_STATUS_CHECKMATE:
            return CHECKMATE_MARK
        if resulting_status == GAME_STATUS_CHECK:
            return CHECK_MARK
        return ""
