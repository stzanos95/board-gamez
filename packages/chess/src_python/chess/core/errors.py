"""
The error hierarchy for the whole engine.
"""


class ChessError(Exception):
    """
    Base class for every error this engine raises.
    """


class NotationError(ChessError):
    """
    Text that was meant to name a square, a piece or a move does not.
    """


class IllegalMoveError(ChessError):
    """
    A move was offered that the rules of chess do not permit.
    """


class BoardStateError(ChessError):
    """
    A board was asked for something its position cannot answer.
    """
