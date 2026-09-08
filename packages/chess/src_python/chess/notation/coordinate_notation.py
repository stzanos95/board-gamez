"""
Moves written as the square left and the square reached: "e2e4".

A promotion appends the new piece's letter: "e7e8q". The form is unambiguous
without knowing the rest of the position, which is why it is what a player types.

A move is read by matching the text against the legal moves, so the parser never
classifies a move itself.
"""

from chess.core.errors import IllegalMoveError, NotationError
from chess.models.move import Move
from chess.models.parsed_coordinate_move import ParsedCoordinateMove
from chess.models.square import Square
from chess.notation.piece_letters import PIECE_TYPES_BY_PROMOTION_LETTER, PieceLetters

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
            if move.promotion_type is None
            else PieceLetters.promotion_letter(move.promotion_type)
        )
        return f"{move.origin.algebraic}{move.destination.algebraic}{promotion}"

    @staticmethod
    def find_move(text: str, legal_moves: tuple[Move, ...]) -> Move:
        """
        The legal move this text names.

        Raises NotationError if the text is not a move, and IllegalMoveError if it
        is well formed but unavailable in this position.
        """
        wanted = CoordinateNotation._normalised(text)
        for move in legal_moves:
            if CoordinateNotation.to_text(move) == wanted:
                return move

        parsed = CoordinateNotation._parsed_move(wanted)
        if parsed.promotion_type is None and any(
            move.origin == parsed.origin and move.destination == parsed.destination
            for move in legal_moves
        ):
            raise IllegalMoveError(
                f"{wanted} reaches {parsed.destination.algebraic} by promoting; "
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

    @staticmethod
    def _parsed_move(text: str) -> ParsedCoordinateMove:
        """
        The squares and promotion the text names, without judging whether the
        move is available.
        """
        origin = Square.from_algebraic(text[:SQUARE_LENGTH])
        destination = Square.from_algebraic(text[SQUARE_LENGTH:PLAIN_LENGTH])
        if len(text) == PLAIN_LENGTH:
            return ParsedCoordinateMove(origin=origin, destination=destination, promotion_type=None)
        letter = text[PLAIN_LENGTH]
        if letter not in PIECE_TYPES_BY_PROMOTION_LETTER:
            raise NotationError(
                f"got promotion {letter!r}, expected one of "
                f"{''.join(PIECE_TYPES_BY_PROMOTION_LETTER)!r}"
            )
        return ParsedCoordinateMove(
            origin=origin,
            destination=destination,
            promotion_type=PIECE_TYPES_BY_PROMOTION_LETTER[letter],
        )
