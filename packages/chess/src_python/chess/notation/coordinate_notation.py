"""
Moves written as the square left and the square reached: "e2e4".

A promotion appends the new piece's letter: "e7e8q". The form is unambiguous
without knowing the rest of the position, which is why it is what a player types.

A move is read by matching the text against the legal moves, so the parser never
classifies a move itself.
"""

from idl.chess.model.move_pb2 import CoordinateMove, Move
from idl.chess.model.piece_pb2 import PIECE_TYPE_UNSPECIFIED

from chess.core.errors import IllegalMoveError, NotationError
from chess.core.squares import Squares
from chess.notation.piece_letters import PIECE_TYPES_BY_PROMOTION_LETTER, PieceLetters
from chess.rules.move_matcher import MoveMatcher

SQUARE_LENGTH = 2
PLAIN_LENGTH = SQUARE_LENGTH * 2
PROMOTING_LENGTH = PLAIN_LENGTH + 1


class CoordinateNotation:
    """
    Reading and writing moves as the square left and the square reached.
    """

    @staticmethod
    def to_text(move: Move) -> str:
        """
        This move written as coordinate text, with a promotion letter if it
        promotes.
        """
        promotion = (
            ""
            if move.promotion_type == PIECE_TYPE_UNSPECIFIED
            else PieceLetters.promotion_letter(move.promotion_type)
        )
        return f"{Squares.algebraic(move.origin)}{Squares.algebraic(move.destination)}{promotion}"

    @staticmethod
    def parse_text(text: str) -> CoordinateMove:
        """
        The squares and promotion the text names, without judging whether the
        move is available.

        Raises NotationError if the text is not a move.
        """
        wanted = CoordinateNotation._normalised(text)
        origin = Squares.from_algebraic(wanted[:SQUARE_LENGTH])
        destination = Squares.from_algebraic(wanted[SQUARE_LENGTH:PLAIN_LENGTH])
        if len(wanted) == PLAIN_LENGTH:
            return CoordinateMove(origin=origin, destination=destination)
        letter = wanted[PLAIN_LENGTH]
        if letter not in PIECE_TYPES_BY_PROMOTION_LETTER:
            raise NotationError(
                f"got promotion {letter!r}, expected one of "
                f"{''.join(PIECE_TYPES_BY_PROMOTION_LETTER)!r}"
            )
        return CoordinateMove(
            origin=origin,
            destination=destination,
            promotion_type=PIECE_TYPES_BY_PROMOTION_LETTER[letter],
        )

    @staticmethod
    def find_move(text: str, legal_moves: tuple[Move, ...]) -> Move:
        """
        The legal move this text names.

        Raises NotationError if the text is not a move, and IllegalMoveError if it
        is well formed but unavailable in this position.
        """
        wanted = CoordinateNotation._normalised(text)
        parsed = CoordinateNotation.parse_text(wanted)
        move = MoveMatcher.get_legal_move(parsed, legal_moves)
        if move is not None:
            return move

        if len(wanted) == PLAIN_LENGTH and any(
            legal.origin == parsed.origin and legal.destination == parsed.destination
            for legal in legal_moves
        ):
            raise IllegalMoveError(
                f"{wanted} reaches {Squares.algebraic(parsed.destination)} by promoting; "
                f"say which piece, as in {wanted}q"
            )
        raise IllegalMoveError(
            f"{wanted} is not legal here; the legal moves are "
            f"{', '.join(sorted(CoordinateNotation.to_text(move) for move in legal_moves))}"
        )

    @staticmethod
    def _normalised(text: str) -> str:
        """
        The text trimmed and lower-cased, rejected here if it is not the right
        length to be a move at all.
        """
        stripped = text.strip().lower()
        if len(stripped) not in (PLAIN_LENGTH, PROMOTING_LENGTH):
            raise NotationError(
                f"got move {text!r}, expected a move such as 'e2e4' or a promotion such as 'e7e8q'"
            )
        return stripped
