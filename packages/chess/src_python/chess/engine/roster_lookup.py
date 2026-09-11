"""
Finding a player in a roster.
"""

from idl.chess.model.game_pb2 import ChessPlayer, PlayerRoster
from idl.chess.model.piece_pb2 import COLOR_WHITE, Color


class RosterLookup:
    """
    Reading a roster by colour.
    """

    @staticmethod
    def get_player(roster: PlayerRoster, color: Color) -> ChessPlayer:
        return roster.white if color == COLOR_WHITE else roster.black
