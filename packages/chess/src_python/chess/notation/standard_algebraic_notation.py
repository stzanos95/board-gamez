"""
Moves written as a scoresheet writes them: "Nf3", "exd5", "O-O", "e8=Q#".

Rendering needs the position's legal moves. A move's name depends on what the
other pieces could have done: "Nf3" becomes "Ngf3" when a second knight also
reaches f3.
"""

from chess.models.algebraic_move_text import AlgebraicMoveText
from chess.models.castling_side import CastlingSide
from chess.models.game_status import GameStatus
from chess.models.move import Move
from chess.models.move_type import MoveType
from chess.models.piece_type import PieceType
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
    def to_text(
        move: Move, legal_moves: tuple[Move, ...], resulting_status: GameStatus
    ) -> AlgebraicMoveText:
        """
        Render a move about to be played from the given position.

        `legal_moves` are the moves available before the move is played.
        `resulting_status` describes the position it leads to.
        """
        suffix = StandardAlgebraicNotation._suffix(resulting_status)
        if move.move_type is MoveType.CASTLE:
            return AlgebraicMoveText(text=StandardAlgebraicNotation._castle_text(move) + suffix)
        body = (
            StandardAlgebraicNotation._pawn_body(move)
            if move.moving_piece_type is PieceType.PAWN
            else StandardAlgebraicNotation._piece_body(move, legal_moves)
        )
        return AlgebraicMoveText(
            text=body + StandardAlgebraicNotation._promotion_text(move) + suffix
        )

    @staticmethod
    def _castle_text(move: Move) -> str:
        if move.castling_side is CastlingSide.QUEENSIDE:
            return QUEENSIDE_CASTLE_TEXT
        return KINGSIDE_CASTLE_TEXT

    @staticmethod
    def _pawn_body(move: Move) -> str:
        if not move.move_type.is_capture:
            return move.destination.algebraic
        # A capturing pawn is always named by the file it left, even when only one
        # pawn could have made the capture.
        return f"{move.origin.file.letter}{CAPTURE_MARK}{move.destination.algebraic}"

    @staticmethod
    def _piece_body(move: Move, legal_moves: tuple[Move, ...]) -> str:
        letter = PieceLetters.notation_letter(move.moving_piece_type)
        capture = CAPTURE_MARK if move.move_type.is_capture else ""
        disambiguation = StandardAlgebraicNotation._disambiguation(move, legal_moves)
        return f"{letter}{disambiguation}{capture}{move.destination.algebraic}"

    @staticmethod
    def _disambiguation(move: Move, legal_moves: tuple[Move, ...]) -> str:
        rivals = tuple(
            other
            for other in legal_moves
            if other.moving_piece_type is move.moving_piece_type
            and other.moving_color is move.moving_color
            and other.destination == move.destination
            and other.origin != move.origin
        )
        if not rivals:
            return ""
        if all(rival.origin.file is not move.origin.file for rival in rivals):
            return move.origin.file.letter
        if all(rival.origin.rank is not move.origin.rank for rival in rivals):
            return move.origin.rank.digit
        return move.origin.algebraic

    @staticmethod
    def _promotion_text(move: Move) -> str:
        if move.promotion_type is None:
            return ""
        return f"{PROMOTION_MARK}{PieceLetters.notation_letter(move.promotion_type)}"

    @staticmethod
    def _suffix(resulting_status: GameStatus) -> str:
        if resulting_status is GameStatus.CHECKMATE:
            return CHECKMATE_MARK
        if resulting_status is GameStatus.CHECK:
            return CHECK_MARK
        return ""
