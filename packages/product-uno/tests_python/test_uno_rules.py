import unittest

from google.protobuf.wrappers_pb2 import StringValue
from idl.game.model.action_pb2 import Action
from idl.game.model.game_result_pb2 import ParticipantOutcome
from idl.game.model.game_state_pb2 import GameState
from idl.game.model.participant_pb2 import ParticipantRole
from idl.game.model.participant_state_pb2 import ParticipantStateKind
from idl.uno.model.card_pb2 import CARD_KIND_WILD, Card
from idl.uno.model.game_pb2 import UnoGame, UnoHand
from idl.uno.model.view_pb2 import UnoView
from uno.deck.deck_builder import DeckBuilder
from uno.engine.uno_engine import HAND_SIZE

from product_uno.adapters.uno_rules_adapters import UnoRulesAdapters
from product_uno.controller.uno_rules import UnoRules
from tests_python.uno_actions import draw_action, packed, pass_action, play, play_action

NOBODY: list[int] = []
SPECTATOR = 0
SEED = 7
ONE = 1
TWO = 2
THREE = 3
ONLOOKER = 9
MINIMUM = 2
MAXIMUM = 10


def seated(participant: int) -> ParticipantRole:
    return ParticipantRole(participant=participant)


THREE_SEATED = (seated(ONE), seated(TWO), seated(THREE))


def require_state(state: GameState | None) -> GameState:
    assert state is not None
    return state


def require_game(state: GameState) -> UnoGame:
    game = UnoRulesAdapters.game_state_to_uno_game(state)
    assert game is not None
    return game


def hand_of(game: UnoGame, participant: int) -> tuple[Card, ...]:
    for hand in game.hands:
        if hand.participant == participant:
            return tuple(hand.cards)
    raise AssertionError(f"no hand for {participant}")


class UnoRulesTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.rules = UnoRules()

    async def new_game(self) -> GameState:
        return require_state(await self.rules.create_game(THREE_SEATED, SEED))

    async def test_a_game_takes_two_to_ten(self) -> None:
        self.assertIsNone(await self.rules.create_game((seated(ONE),), SEED))
        self.assertIsNotNone(await self.rules.create_game((seated(ONE), seated(TWO)), SEED))
        ten = tuple(seated(number) for number in range(1, MAXIMUM + 1))
        self.assertIsNotNone(await self.rules.create_game(ten, SEED))
        eleven = (*ten, seated(MAXIMUM + 1))
        self.assertIsNone(await self.rules.create_game(eleven, SEED))

    async def test_the_bounds_say_two_to_ten(self) -> None:
        bounds = await self.rules.read_bounds()
        self.assertEqual((bounds.minimum, bounds.maximum), (MINIMUM, MAXIMUM))

    async def test_the_lowest_number_acts_first_whatever_the_order_given(self) -> None:
        state = require_state(
            await self.rules.create_game((seated(THREE), seated(ONE), seated(TWO)), SEED)
        )
        self.assertEqual(list(state.participants_to_act), [ONE])
        self.assertEqual(
            [hand.participant for hand in require_game(state).hands], [ONE, TWO, THREE]
        )

    async def test_a_new_game_deals_everyone_seven_and_has_no_result(self) -> None:
        state = await self.new_game()
        self.assertFalse(state.HasField("result"))
        game = require_game(state)
        for participant in (ONE, TWO, THREE):
            self.assertEqual(len(hand_of(game, participant)), HAND_SIZE)

    async def test_the_same_seed_deals_the_same_game(self) -> None:
        self.assertEqual(await self.new_game(), await self.new_game())

    async def test_drawing_keeps_the_turn_and_passing_moves_it_on(self) -> None:
        state = await self.new_game()
        drawn = require_state(await self.rules.apply_action(state, draw_action(ONE)))
        self.assertEqual(list(drawn.participants_to_act), [ONE])
        self.assertEqual(len(hand_of(require_game(drawn), ONE)), HAND_SIZE + 1)
        passed = require_state(await self.rules.apply_action(drawn, pass_action(ONE)))
        self.assertEqual(list(passed.participants_to_act), [TWO])
        # The state handed in is untouched: the rules answer a new one.
        self.assertEqual(list(state.participants_to_act), [ONE])

    async def test_the_wrong_participant_is_refused(self) -> None:
        state = await self.new_game()
        self.assertIsNone(await self.rules.apply_action(state, draw_action(TWO)))
        self.assertIsNone(await self.rules.apply_action(state, draw_action(ONLOOKER)))

    async def test_a_card_not_held_is_refused(self) -> None:
        state = await self.new_game()
        held = hand_of(require_game(state), ONE)
        stray = next(card for card in DeckBuilder.build_deck() if card not in held)
        self.assertIsNone(await self.rules.apply_action(state, play_action(ONE, stray)))

    async def test_a_payload_that_is_not_a_uno_action_is_refused(self) -> None:
        state = await self.new_game()
        stray = Action(participant=ONE)
        stray.payload.Pack(StringValue(value="draw"))
        self.assertIsNone(await self.rules.apply_action(state, stray))

    async def test_a_state_that_is_not_a_uno_game_is_refused(self) -> None:
        stray = GameState(participants_to_act=[ONE])
        stray.payload.Pack(StringValue(value="not uno"))
        self.assertIsNone(await self.rules.apply_action(stray, draw_action(ONE)))

    async def test_withdrawing_leaves_the_others_playing(self) -> None:
        state = await self.new_game()
        after = require_state(await self.rules.withdraw_participant(state, ONE))
        self.assertEqual(list(after.participants_to_act), [TWO])
        self.assertFalse(after.HasField("result"))
        self.assertIsNone(await self.rules.withdraw_participant(after, ONE))
        self.assertIsNone(await self.rules.withdraw_participant(state, ONLOOKER))

    async def test_the_last_player_left_wins(self) -> None:
        state = await self.new_game()
        after = require_state(await self.rules.withdraw_participant(state, ONE))
        after = require_state(await self.rules.withdraw_participant(after, THREE))
        self.assertEqual(list(after.participants_to_act), NOBODY)
        outcomes = {item.participant: item.outcome for item in after.result.participant_items}
        self.assertEqual(outcomes[TWO], ParticipantOutcome.PARTICIPANT_OUTCOME_WON)
        self.assertEqual(outcomes[ONE], ParticipantOutcome.PARTICIPANT_OUTCOME_LOST)
        self.assertEqual(outcomes[THREE], ParticipantOutcome.PARTICIPANT_OUTCOME_LOST)

    async def test_nothing_can_be_played_once_the_game_is_over(self) -> None:
        state = await self.new_game()
        after = require_state(await self.rules.withdraw_participant(state, ONE))
        after = require_state(await self.rules.withdraw_participant(after, THREE))
        self.assertIsNone(await self.rules.apply_action(after, draw_action(TWO)))

    async def test_a_player_sees_their_own_hand_and_no_other(self) -> None:
        state = await self.new_game()
        game = require_game(state)
        for participant in (ONE, TWO, THREE):
            with self.subTest(participant=participant):
                view = UnoView()
                self.assertTrue((await self.rules.read_view(state, participant)).Unpack(view))
                self.assertEqual(
                    [shown.card for shown in view.hand], list(hand_of(game, participant))
                )
                self.assertEqual([player.card_count for player in view.players], [7, 7, 7])
                self.assertEqual(view.participant_to_act, ONE)
                self.assertEqual(view.may_draw, participant == ONE)

    async def test_a_spectator_sees_no_hand(self) -> None:
        state = await self.new_game()
        view = UnoView()
        self.assertTrue((await self.rules.read_view(state, SPECTATOR)).Unpack(view))
        self.assertEqual(len(view.hand), 0)
        self.assertTrue(view.HasField("top_card"))

    async def test_every_participant_is_shown_holding_their_cards(self) -> None:
        state = await self.new_game()
        self.assertEqual(
            [status.participant for status in state.participant_statuses], [ONE, TWO, THREE]
        )
        for status in state.participant_statuses:
            self.assertEqual(
                [(item.kind, item.count) for item in status.states],
                [(ParticipantStateKind.PARTICIPANT_STATE_KIND_HOLDING, HAND_SIZE)],
            )

    async def test_a_hand_down_to_one_card_is_shown_as_the_last_one(self) -> None:
        status = UnoRulesAdapters.uno_hand_to_participant_status(
            UnoHand(participant=ONE, cards=[Card(kind=CARD_KIND_WILD)])
        )
        self.assertEqual(
            [item.kind for item in status.states],
            [
                ParticipantStateKind.PARTICIPANT_STATE_KIND_HOLDING,
                ParticipantStateKind.PARTICIPANT_STATE_KIND_LAST_ONE,
            ],
        )

    async def test_a_player_who_left_is_shown_withdrawn(self) -> None:
        state = await self.new_game()
        after = require_state(await self.rules.withdraw_participant(state, ONE))
        self.assertEqual(
            [item.kind for item in after.participant_statuses[0].states],
            [ParticipantStateKind.PARTICIPANT_STATE_KIND_WITHDRAWN],
        )

    async def test_no_state_carries_a_deadline(self) -> None:
        state = await self.new_game()
        self.assertFalse(state.HasField("acts_within"))
        self.assertIsNone(await self.rules.expire_deadline(state))

    async def test_an_action_survives_packing(self) -> None:
        action = play_action(ONE, Card(kind=CARD_KIND_WILD))
        unpacked = UnoRulesAdapters.action_to_uno_action(action)
        assert unpacked is not None
        self.assertEqual(unpacked.play.card.kind, CARD_KIND_WILD)
        self.assertEqual(packed(unpacked), action.payload)
        self.assertEqual(unpacked, play(Card(kind=CARD_KIND_WILD)))
