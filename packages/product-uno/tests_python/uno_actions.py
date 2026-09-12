"""
UNO actions as a client packs them, for tests.
"""

from google.protobuf import any_pb2
from idl.game.model.action_pb2 import Action
from idl.uno.model.action_pb2 import CardDraw, CardPlay, TurnPass, UnoAction
from idl.uno.model.card_pb2 import CARD_COLOR_UNSPECIFIED, Card, CardColor

# `pass` is a keyword, so the generated message exposes the field by name only.
PASS_FIELD = "pass"


def play_action(
    participant: int, card: Card, chosen_color: CardColor = CARD_COLOR_UNSPECIFIED
) -> Action:
    return Action(participant=participant, payload=packed(play(card, chosen_color)))


def draw_action(participant: int) -> Action:
    return Action(participant=participant, payload=packed(draw()))


def pass_action(participant: int) -> Action:
    return Action(participant=participant, payload=packed(pass_turn()))


def play(card: Card, chosen_color: CardColor = CARD_COLOR_UNSPECIFIED) -> UnoAction:
    return UnoAction(play=CardPlay(card=card, chosen_color=chosen_color))


def draw() -> UnoAction:
    return UnoAction(draw=CardDraw())


def pass_turn() -> UnoAction:
    action = UnoAction()
    getattr(action, PASS_FIELD).CopyFrom(TurnPass())
    return action


def packed(action: UnoAction) -> any_pb2.Any:
    payload = any_pb2.Any()
    payload.Pack(action)
    return payload
