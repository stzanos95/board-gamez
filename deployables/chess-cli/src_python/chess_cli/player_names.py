"""
What each participant is called at this terminal.

The engine knows a player by participant number and colour. The names come from
the settings file, and this is where a number becomes a name.
"""

from dataclasses import dataclass

from idl.chess.model.game_pb2 import ChessPlayer

from chess_cli.cli_settings import PlayerSettings

WHITE_PARTICIPANT = 1
BLACK_PARTICIPANT = 2

NamesByParticipant = dict[int, str]


@dataclass(frozen=True, slots=True)
class PlayerNames:
    """
    A name for each participant in the game.
    """

    names_by_participant: NamesByParticipant

    @staticmethod
    def from_settings(players: PlayerSettings) -> "PlayerNames":
        return PlayerNames(
            names_by_participant={
                WHITE_PARTICIPANT: players.white_name,
                BLACK_PARTICIPANT: players.black_name,
            }
        )

    def get_name(self, player: ChessPlayer) -> str:
        return self.names_by_participant[player.participant]
