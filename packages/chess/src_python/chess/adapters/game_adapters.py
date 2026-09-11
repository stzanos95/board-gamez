"""
A game, between the engine and the schema's record of it.

The record carries the position, the history and everything the engine derives
from them. Reading a record back recomputes the legal moves and the status from
the position, so a record cannot claim a move the position does not allow.
"""

from idl.chess.model.game_pb2 import ChessGame, ChessTurnHistory, PlayerRoster
from idl.chess.model.piece_pb2 import COLOR_UNSPECIFIED

from chess.adapters.board_adapters import BoardAdapters
from chess.engine.chess_engine import ChessEngine
from chess.rules.game_status_evaluator import GameStatusEvaluator
from chess.rules.legal_move_generator import LegalMoveGenerator


class GameAdapters:
    """
    A whole game, converted between the engine and the schema's record.
    """

    @staticmethod
    def engine_to_chess_game(engine: ChessEngine) -> ChessGame:
        return ChessGame(
            roster=engine.roster,
            state=BoardAdapters.state_to_message(engine.state),
            history=ChessTurnHistory(turns=engine.turns, position_keys=engine.position_keys),
            legal_moves=engine.legal_moves,
            status=engine.status,
            resigning_color=engine.resigning_color,
            result=engine.result,
        )

    @staticmethod
    def chess_game_to_engine(game: ChessGame) -> ChessEngine:
        """
        The engine holds copies of the record's roster and turns, so a record
        changed after this call changes nothing in the engine.
        """
        roster = PlayerRoster()
        roster.CopyFrom(game.roster)
        history = ChessTurnHistory()
        history.CopyFrom(game.history)
        state = BoardAdapters.message_to_state(game.state)
        position_keys = tuple(history.position_keys)
        legal_moves = LegalMoveGenerator.moves_for_side_to_move(state)
        return ChessEngine(
            roster=roster,
            state=state,
            turns=tuple(history.turns),
            position_keys=position_keys,
            legal_moves=legal_moves,
            status=GameStatusEvaluator.evaluate(
                state=state, position_keys=position_keys, legal_moves=legal_moves
            ),
            resigning_color=(
                None if game.resigning_color == COLOR_UNSPECIFIED else game.resigning_color
            ),
        )
