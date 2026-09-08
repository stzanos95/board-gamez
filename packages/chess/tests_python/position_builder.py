"""
Building positions for tests.

`board_with` names pieces one at a time, and is what most tests use.

`board_from_placement` reads the compact placement text the standard perft
positions are published in, so a reference string can be copied verbatim instead
of transcribed piece by piece. The engine itself cannot read this format.
"""

from collections.abc import Iterable

from chess.board.chess_board_state import ChessBoardState
from chess.models.castling_right import CastlingRight
from chess.models.castling_rights import CastlingRights
from chess.models.castling_side import CastlingSide
from chess.models.color import Color
from chess.models.move import Move
from chess.models.piece_type import PieceType
from chess.models.square import Square
from chess.pieces.base_piece import BasePiece
from chess.pieces.piece_factory import PieceFactory

PLACEMENT_RANK_SEPARATOR = "/"
TOP_RANK_DIGIT = 8
FILE_LETTERS = "abcdefgh"

PLACEMENT_LETTERS: dict[str, PieceType] = {
    "p": PieceType.PAWN,
    "n": PieceType.KNIGHT,
    "b": PieceType.BISHOP,
    "r": PieceType.ROOK,
    "q": PieceType.QUEEN,
    "k": PieceType.KING,
}

CASTLING_LETTERS: dict[str, CastlingSide] = {
    "k": CastlingSide.KINGSIDE,
    "q": CastlingSide.QUEENSIDE,
}


def white(piece_type: PieceType, square: str) -> BasePiece:
    return PieceFactory.create_piece(
        piece_type=piece_type, color=Color.WHITE, square=Square.from_algebraic(square)
    )


def black(piece_type: PieceType, square: str) -> BasePiece:
    return PieceFactory.create_piece(
        piece_type=piece_type, color=Color.BLACK, square=Square.from_algebraic(square)
    )


def board_with(
    pieces: Iterable[BasePiece],
    side_to_move: Color = Color.WHITE,
    castling_rights: CastlingRights | None = None,
    en_passant_target: str | None = None,
    halfmove_clock: int = 0,
) -> ChessBoardState:
    return ChessBoardState.from_pieces(
        pieces=pieces,
        side_to_move=side_to_move,
        castling_rights=castling_rights,
        en_passant_target=(
            None if en_passant_target is None else Square.from_algebraic(en_passant_target)
        ),
        halfmove_clock=halfmove_clock,
    )


def rights_from_text(text: str) -> CastlingRights:
    """
    Read castling rights written as in the reference positions: "KQkq".
    """
    return CastlingRights(
        available=frozenset(
            CastlingRight(
                color=Color.WHITE if letter.isupper() else Color.BLACK,
                side=CASTLING_LETTERS[letter.lower()],
            )
            for letter in text
        )
    )


def board_from_placement(
    placement: str,
    side_to_move: Color = Color.WHITE,
    castling_text: str = "",
    en_passant_target: str | None = None,
) -> ChessBoardState:
    pieces: list[BasePiece] = []
    for row, rank_text in enumerate(placement.split(PLACEMENT_RANK_SEPARATOR)):
        rank_digit = str(TOP_RANK_DIGIT - row)
        file_index = 0
        for letter in rank_text:
            if letter.isdigit():
                file_index += int(letter)
                continue
            square = Square.from_algebraic(f"{FILE_LETTERS[file_index]}{rank_digit}")
            pieces.append(
                PieceFactory.create_piece(
                    piece_type=PLACEMENT_LETTERS[letter.lower()],
                    color=Color.WHITE if letter.isupper() else Color.BLACK,
                    square=square,
                )
            )
            file_index += 1
    return board_with(
        pieces=pieces,
        side_to_move=side_to_move,
        castling_rights=rights_from_text(castling_text),
        en_passant_target=en_passant_target,
    )


def destinations(moves: Iterable[Move]) -> set[str]:
    return {move.destination.algebraic for move in moves}
