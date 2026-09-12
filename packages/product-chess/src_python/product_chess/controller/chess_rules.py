"""
The rules of chess, as the platform asks them.

The one place that decides what a participant means in chess: the participant
seated as White plays White, the one seated as Black plays Black, and a game
takes exactly one of each.
"""

from chess.adapters.game_adapters import GameAdapters
from chess.engine.chess_engine import ChessEngine
from chess.rules.move_matcher import MoveMatcher
from game.controller.base_rules import BaseRules
from google.protobuf import any_pb2
from idl.chess.model.action_pb2 import ChessAction
from idl.chess.model.piece_pb2 import COLOR_UNSPECIFIED
from idl.game.model.action_pb2 import Action
from idl.game.model.game_spec_pb2 import ParticipantBounds
from idl.game.model.game_state_pb2 import GameState
from idl.game.model.participant_pb2 import ParticipantRole

from product_chess.adapters.chess_rules_adapters import ChessRulesAdapters
from product_chess.adapters.chess_session_adapters import ChessSessionAdapters

CHESS_PARTICIPANT_COUNT = 2


class ChessRules(BaseRules):
    """
    Every question the platform asks a game, answered for chess.

    Every viewer is shown the whole game: chess has no hidden information.
    Nothing in chess is drawn by chance, so the seed is not read, and no state
    runs out, so no deadline is ever expired.
    """

    async def create_game(
        self, participant_roles: tuple[ParticipantRole, ...], seed: int
    ) -> GameState | None:
        if len(participant_roles) != CHESS_PARTICIPANT_COUNT:
            return None
        roster = ChessRulesAdapters.participant_roles_to_player_roster(participant_roles)
        if roster is None:
            return None
        engine = ChessEngine.new_game(
            white_participant=roster.white.participant,
            black_participant=roster.black.participant,
        )
        return ChessRulesAdapters.engine_to_game_state(engine)

    async def apply_action(self, state: GameState, action: Action) -> GameState | None:
        game = ChessRulesAdapters.game_state_to_chess_game(state)
        if game is None:
            return None
        engine = GameAdapters.chess_game_to_engine(game)
        if engine.is_over or action.participant != engine.active_player.participant:
            return None
        chess_action = ChessRulesAdapters.action_to_chess_action(action)
        if chess_action is None:
            return None
        advanced = ChessRules._get_advanced_engine(engine, chess_action)
        if advanced is None:
            return None
        return ChessRulesAdapters.engine_to_game_state(advanced)

    async def withdraw_participant(self, state: GameState, participant: int) -> GameState | None:
        """
        A participant who leaves resigns, and the other side wins.
        """
        game = ChessRulesAdapters.game_state_to_chess_game(state)
        if game is None:
            return None
        color = ChessSessionAdapters.participant_to_color(game.roster, participant)
        if color == COLOR_UNSPECIFIED:
            return None
        engine = GameAdapters.chess_game_to_engine(game)
        return ChessRulesAdapters.engine_to_game_state(engine.resign(color))

    async def read_view(self, state: GameState, participant: int) -> any_pb2.Any:
        view = any_pb2.Any()
        view.CopyFrom(state.payload)
        return view

    async def expire_deadline(self, state: GameState) -> GameState | None:
        return None

    async def read_bounds(self) -> ParticipantBounds:
        return ParticipantBounds(minimum=CHESS_PARTICIPANT_COUNT, maximum=CHESS_PARTICIPANT_COUNT)

    @staticmethod
    def _get_advanced_engine(engine: ChessEngine, chess_action: ChessAction) -> ChessEngine | None:
        """
        The game after this action, or None when the action names no legal move.
        """
        if chess_action.HasField("move"):
            move = MoveMatcher.get_legal_move(chess_action.move, engine.legal_moves)
            return None if move is None else engine.play(move)
        if chess_action.HasField("resignation"):
            return engine.resign(engine.state.side_to_move)
        return None
