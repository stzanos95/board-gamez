"""
Chess actions as a client packs them, for tests.
"""

from chess.notation.coordinate_notation import CoordinateNotation
from google.protobuf import any_pb2
from idl.chess.model.action_pb2 import ChessAction, Resignation
from idl.game.model.action_pb2 import Action


def move_action(participant: int, text: str) -> Action:
    return Action(participant=participant, payload=packed(move(text)))


def resignation_action(participant: int) -> Action:
    return Action(participant=participant, payload=packed(resignation()))


def move(text: str) -> ChessAction:
    return ChessAction(move=CoordinateNotation.parse_text(text))


def resignation() -> ChessAction:
    return ChessAction(resignation=Resignation())


def packed(action: ChessAction) -> any_pb2.Any:
    payload = any_pb2.Any()
    payload.Pack(action)
    return payload
