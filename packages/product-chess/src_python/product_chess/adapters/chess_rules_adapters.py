"""
Chess, between the platform's types and the game's own.

The platform carries a game's state and a participant's action opaquely. Every
conversion between what the platform holds and what the engine takes runs
here, one named method per direction.
"""

from chess.adapters.game_adapters import GameAdapters
from chess.engine.chess_engine import ChessEngine
from google.protobuf import any_pb2
from idl.chess.model import game_pb2
from idl.chess.model.action_pb2 import ChessAction
from idl.chess.model.piece_pb2 import COLOR_BLACK, COLOR_WHITE, Color
from idl.game.model.action_pb2 import Action
from idl.game.model.game_result_pb2 import GameResult, ParticipantOutcome, ParticipantResult
from idl.game.model.game_state_pb2 import GameState
from idl.game.model.participant_pb2 import ParticipantRole

from product_chess.adapters.chess_seat_adapters import ChessSeatAdapters

NOBODY_TO_ACT: tuple[int, ...] = ()


class ChessRulesAdapters:
    """
    Every RulesService message and every platform type, converted to what chess
    takes and back.
    """

    # --- the platform's state and action, to chess's ------------------------

    @staticmethod
    def game_state_to_chess_game(state: GameState) -> game_pb2.ChessGame | None:
        """
        The chess game the state carries, or None when the payload is not one.
        """
        game = game_pb2.ChessGame()
        if not state.payload.Unpack(game):
            return None
        return game

    @staticmethod
    def action_to_chess_action(action: Action) -> ChessAction | None:
        """
        The chess action the action carries, or None when the payload is not one.
        """
        chess_action = ChessAction()
        if not action.payload.Unpack(chess_action):
            return None
        return chess_action

    # --- the platform's roles, to chess's roster ----------------------------

    @staticmethod
    def participant_roles_to_player_roster(
        participant_roles: tuple[ParticipantRole, ...],
    ) -> game_pb2.PlayerRoster | None:
        """
        The roster these roles seat, or None unless exactly one participant is
        seated as White and exactly one as Black.
        """
        white = ChessRulesAdapters._get_participants_seated_as(participant_roles, COLOR_WHITE)
        black = ChessRulesAdapters._get_participants_seated_as(participant_roles, COLOR_BLACK)
        if len(white) != 1 or len(black) != 1:
            return None
        return game_pb2.PlayerRoster(
            white=game_pb2.ChessPlayer(color=COLOR_WHITE, participant=white[0]),
            black=game_pb2.ChessPlayer(color=COLOR_BLACK, participant=black[0]),
        )

    @staticmethod
    def _get_participants_seated_as(
        participant_roles: tuple[ParticipantRole, ...], color: Color
    ) -> tuple[int, ...]:
        return tuple(
            participant_role.participant
            for participant_role in participant_roles
            if ChessSeatAdapters.role_to_color(participant_role.role) == color
        )

    # --- the engine, to the platform's state -------------------------------

    @staticmethod
    def engine_to_game_state(engine: ChessEngine) -> GameState:
        """
        The game as the platform holds it: the whole chess game packed, who acts
        next, and the result once there is one. Chess has no clock here, so no
        state runs out.
        """
        result = engine.result
        return GameState(
            payload=ChessRulesAdapters.chess_game_to_payload(
                GameAdapters.engine_to_chess_game(engine)
            ),
            participants_to_act=(
                NOBODY_TO_ACT if engine.is_over else (engine.active_player.participant,)
            ),
            result=(
                None
                if result is None
                else ChessRulesAdapters.chess_result_to_game_result(result, engine.roster)
            ),
        )

    @staticmethod
    def chess_game_to_payload(game: game_pb2.ChessGame) -> any_pb2.Any:
        payload = any_pb2.Any()
        payload.Pack(game)
        return payload

    @staticmethod
    def chess_result_to_game_result(
        result: game_pb2.GameResult, roster: game_pb2.PlayerRoster
    ) -> GameResult:
        """
        One entry per side. A game with a winner scores the other side as lost;
        a draw scores both sides as drawn.
        """
        players = (roster.white, roster.black)
        if not result.HasField("winner"):
            return GameResult(
                participant_items=[
                    ParticipantResult(
                        participant=player.participant,
                        outcome=ParticipantOutcome.PARTICIPANT_OUTCOME_DRAW,
                    )
                    for player in players
                ]
            )
        return GameResult(
            participant_items=[
                ParticipantResult(
                    participant=player.participant,
                    outcome=(
                        ParticipantOutcome.PARTICIPANT_OUTCOME_WON
                        if player.participant == result.winner.participant
                        else ParticipantOutcome.PARTICIPANT_OUTCOME_LOST
                    ),
                )
                for player in players
            ]
        )
