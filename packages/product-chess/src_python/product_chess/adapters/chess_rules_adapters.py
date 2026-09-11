"""
Chess, between the platform's types and the game's own.

The platform carries a game's state and a participant's action opaquely, and
asks the rules through RulesService. Every conversion between what the platform
holds and what the engine takes runs here, one named method per direction.
"""

from chess.adapters.game_adapters import GameAdapters
from chess.engine.chess_engine import ChessEngine
from google.protobuf import any_pb2
from idl.chess.model import game_pb2
from idl.chess.model.action_pb2 import ChessAction
from idl.game.dto import rules_pb2
from idl.game.model.action_pb2 import Action
from idl.game.model.game_result_pb2 import GameResult, ParticipantOutcome, ParticipantResult
from idl.game.model.game_spec_pb2 import ParticipantBounds
from idl.game.model.game_state_pb2 import GameState

NOBODY_TO_ACT = 0


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

    # --- the engine, to the platform's state -------------------------------

    @staticmethod
    def engine_to_game_state(engine: ChessEngine) -> GameState:
        """
        The game as the platform holds it: the whole chess game packed, who acts
        next, and the result once there is one.
        """
        result = engine.result
        return GameState(
            payload=ChessRulesAdapters.chess_game_to_payload(
                GameAdapters.engine_to_chess_game(engine)
            ),
            participant_to_act=NOBODY_TO_ACT
            if engine.is_over
            else engine.active_player.participant,
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

    # --- a request, to the arguments an operation takes ----------------------

    @staticmethod
    def create_request_to_participant_count(request: rules_pb2.CreateGameRequest) -> int:
        return request.participant_count

    @staticmethod
    def apply_request_to_state(request: rules_pb2.ApplyActionRequest) -> GameState:
        return request.state

    @staticmethod
    def apply_request_to_action(request: rules_pb2.ApplyActionRequest) -> Action:
        return request.action

    @staticmethod
    def view_request_to_state(request: rules_pb2.ReadViewRequest) -> GameState:
        return request.state

    @staticmethod
    def view_request_to_participant(request: rules_pb2.ReadViewRequest) -> int:
        return request.participant

    # --- what an operation answers, to a response ----------------------------

    @staticmethod
    def game_state_to_create_response(state: GameState | None) -> rules_pb2.CreateGameResponse:
        """
        An unset state is how the schema says the game does not take that many.
        """
        return rules_pb2.CreateGameResponse(state=state)

    @staticmethod
    def game_state_to_apply_response(state: GameState | None) -> rules_pb2.ApplyActionResponse:
        """
        An unset state is how the schema says the action was not legal.
        """
        return rules_pb2.ApplyActionResponse(state=state)

    @staticmethod
    def view_to_view_response(view: any_pb2.Any) -> rules_pb2.ReadViewResponse:
        return rules_pb2.ReadViewResponse(view=view)

    @staticmethod
    def bounds_to_bounds_response(bounds: ParticipantBounds) -> rules_pb2.ReadBoundsResponse:
        return rules_pb2.ReadBoundsResponse(bounds=bounds)
