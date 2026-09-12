import unittest

from idl.uno.model.action_pb2 import CardDraw, CardPlay, TurnPass, UnoAction
from idl.uno.model.card_pb2 import (
    CARD_COLOR_BLUE,
    CARD_COLOR_GREEN,
    CARD_COLOR_RED,
    CARD_COLOR_UNSPECIFIED,
    CARD_COLOR_YELLOW,
    CARD_KIND_NUMBER,
    Card,
    CardColor,
)
from idl.uno.model.game_pb2 import (
    PLAY_DIRECTION_CLOCKWISE,
    PLAY_DIRECTION_COUNTERCLOCKWISE,
    UNO_RESULT_REASON_HAND_EMPTIED,
    UNO_RESULT_REASON_OTHERS_WITHDREW,
    UnoGame,
)

from tests_python.game_builder import (
    GameBuilder,
    draw_two,
    number,
    reverse,
    skip,
    wild,
    wild_draw_four,
)
from uno.deck.deck_builder import DECK_SIZE
from uno.engine.uno_engine import HAND_SIZE, UnoEngine
from uno.engine.view_projector import ViewProjector

SEED = 7
ONE = 1
TWO = 2
THREE = 3
ONLOOKER = 9
NOBODY = 0
THREE_PLAYERS = (ONE, TWO, THREE)
TEN_PLAYERS = tuple(range(1, 11))
ELEVEN_PLAYERS = tuple(range(1, 12))
FIRST_DISCARD = 1
# `pass` is a keyword, so the generated message exposes the field by name only.
PASS_FIELD = "pass"


def play(card: Card, chosen_color: CardColor = CARD_COLOR_UNSPECIFIED) -> UnoAction:
    return UnoAction(play=CardPlay(card=card, chosen_color=chosen_color))


def draw() -> UnoAction:
    return UnoAction(draw=CardDraw())


def pass_turn() -> UnoAction:
    action = UnoAction()
    getattr(action, PASS_FIELD).CopyFrom(TurnPass())
    return action


def require(game: UnoGame | None) -> UnoGame:
    assert game is not None
    return game


def cards_held(game: UnoGame, participant: int) -> int:
    for hand in game.hands:
        if hand.participant == participant:
            return len(hand.cards)
    raise AssertionError(f"no hand for {participant}")


class NewGameTest(unittest.TestCase):
    def test_everyone_is_dealt_seven_and_a_number_card_is_turned_over(self) -> None:
        game = require(UnoEngine.new_game(THREE_PLAYERS, SEED))
        for participant in THREE_PLAYERS:
            self.assertEqual(cards_held(game, participant), HAND_SIZE)
        self.assertEqual(len(game.discard_pile), FIRST_DISCARD)
        top = game.discard_pile[0]
        self.assertEqual(top.kind, CARD_KIND_NUMBER)
        self.assertEqual(game.active_color, top.color)
        self.assertEqual(game.participant_to_act, ONE)
        self.assertEqual(game.direction, PLAY_DIRECTION_CLOCKWISE)
        self.assertEqual(
            len(game.draw_pile) + len(game.discard_pile) + HAND_SIZE * len(THREE_PLAYERS),
            DECK_SIZE,
        )

    def test_the_deal_is_fixed_by_the_seed(self) -> None:
        self.assertEqual(
            UnoEngine.new_game(THREE_PLAYERS, SEED), UnoEngine.new_game(THREE_PLAYERS, SEED)
        )
        self.assertNotEqual(
            UnoEngine.new_game(THREE_PLAYERS, SEED), UnoEngine.new_game(THREE_PLAYERS, SEED + 1)
        )

    def test_a_game_takes_two_to_ten(self) -> None:
        self.assertIsNone(UnoEngine.new_game((ONE,), SEED))
        self.assertIsNotNone(UnoEngine.new_game((ONE, TWO), SEED))
        self.assertIsNotNone(UnoEngine.new_game(TEN_PLAYERS, SEED))
        self.assertIsNone(UnoEngine.new_game(ELEVEN_PLAYERS, SEED))


class PlayTest(unittest.TestCase):
    def setUp(self) -> None:
        self.game = GameBuilder.build(
            hands={
                ONE: (
                    number(CARD_COLOR_RED, 5),
                    number(CARD_COLOR_BLUE, 9),
                    skip(CARD_COLOR_RED),
                    reverse(CARD_COLOR_RED),
                    draw_two(CARD_COLOR_RED),
                    wild(),
                    wild_draw_four(),
                ),
                TWO: (number(CARD_COLOR_GREEN, 1), number(CARD_COLOR_GREEN, 2)),
                THREE: (number(CARD_COLOR_YELLOW, 1), number(CARD_COLOR_YELLOW, 2)),
            },
            draw_pile=(
                number(CARD_COLOR_GREEN, 3),
                number(CARD_COLOR_GREEN, 4),
                number(CARD_COLOR_GREEN, 5),
                number(CARD_COLOR_GREEN, 6),
            ),
            top=number(CARD_COLOR_RED, 7),
            active_color=CARD_COLOR_RED,
            participant_to_act=ONE,
        )

    def test_a_number_card_passes_the_turn(self) -> None:
        after = require(UnoEngine.apply_action(self.game, ONE, play(number(CARD_COLOR_RED, 5))))
        self.assertEqual(after.participant_to_act, TWO)
        self.assertEqual(after.discard_pile[-1], number(CARD_COLOR_RED, 5))
        self.assertEqual(cards_held(after, ONE), 6)
        # The game handed in is untouched.
        self.assertEqual(self.game.participant_to_act, ONE)
        self.assertEqual(cards_held(self.game, ONE), 7)

    def test_a_card_that_does_not_follow_is_refused(self) -> None:
        self.assertIsNone(UnoEngine.apply_action(self.game, ONE, play(number(CARD_COLOR_BLUE, 9))))

    def test_a_card_not_in_the_hand_is_refused(self) -> None:
        self.assertIsNone(UnoEngine.apply_action(self.game, ONE, play(number(CARD_COLOR_RED, 1))))

    def test_only_the_participant_to_act_may_act(self) -> None:
        self.assertIsNone(UnoEngine.apply_action(self.game, TWO, play(number(CARD_COLOR_GREEN, 1))))
        self.assertIsNone(UnoEngine.apply_action(self.game, ONLOOKER, draw()))

    def test_a_skip_passes_over_the_next_player(self) -> None:
        after = require(UnoEngine.apply_action(self.game, ONE, play(skip(CARD_COLOR_RED))))
        self.assertEqual(after.participant_to_act, THREE)

    def test_a_reverse_turns_play_the_other_way(self) -> None:
        after = require(UnoEngine.apply_action(self.game, ONE, play(reverse(CARD_COLOR_RED))))
        self.assertEqual(after.direction, PLAY_DIRECTION_COUNTERCLOCKWISE)
        self.assertEqual(after.participant_to_act, THREE)

    def test_a_draw_two_makes_the_next_player_draw_and_lose_their_turn(self) -> None:
        after = require(UnoEngine.apply_action(self.game, ONE, play(draw_two(CARD_COLOR_RED))))
        self.assertEqual(cards_held(after, TWO), 4)
        self.assertEqual(after.participant_to_act, THREE)
        self.assertEqual(len(after.draw_pile), 2)

    def test_a_wild_names_the_colour_to_follow(self) -> None:
        after = require(UnoEngine.apply_action(self.game, ONE, play(wild(), CARD_COLOR_GREEN)))
        self.assertEqual(after.active_color, CARD_COLOR_GREEN)
        self.assertEqual(after.participant_to_act, TWO)

    def test_a_wild_without_a_colour_is_refused(self) -> None:
        self.assertIsNone(UnoEngine.apply_action(self.game, ONE, play(wild())))

    def test_a_coloured_card_with_a_chosen_colour_is_refused(self) -> None:
        self.assertIsNone(
            UnoEngine.apply_action(self.game, ONE, play(number(CARD_COLOR_RED, 5), CARD_COLOR_BLUE))
        )

    def test_a_wild_draw_four_is_refused_while_the_active_colour_is_held(self) -> None:
        self.assertIsNone(
            UnoEngine.apply_action(self.game, ONE, play(wild_draw_four(), CARD_COLOR_GREEN))
        )

    def test_a_wild_draw_four_makes_the_next_player_draw_four(self) -> None:
        game = GameBuilder.build(
            hands={
                ONE: (wild_draw_four(), number(CARD_COLOR_BLUE, 1)),
                TWO: (number(CARD_COLOR_GREEN, 1),),
                THREE: (number(CARD_COLOR_YELLOW, 1),),
            },
            draw_pile=tuple(number(CARD_COLOR_GREEN, value) for value in range(5)),
            top=number(CARD_COLOR_RED, 7),
            active_color=CARD_COLOR_RED,
            participant_to_act=ONE,
        )
        after = require(UnoEngine.apply_action(game, ONE, play(wild_draw_four(), CARD_COLOR_BLUE)))
        self.assertEqual(cards_held(after, TWO), 5)
        self.assertEqual(after.participant_to_act, THREE)
        self.assertEqual(after.active_color, CARD_COLOR_BLUE)


class DrawAndPassTest(unittest.TestCase):
    def setUp(self) -> None:
        self.game = GameBuilder.build(
            hands={
                ONE: (number(CARD_COLOR_BLUE, 9),),
                TWO: (number(CARD_COLOR_GREEN, 1),),
                THREE: (number(CARD_COLOR_YELLOW, 1),),
            },
            draw_pile=(number(CARD_COLOR_RED, 2), number(CARD_COLOR_GREEN, 4)),
            top=number(CARD_COLOR_RED, 7),
            active_color=CARD_COLOR_RED,
            participant_to_act=ONE,
        )

    def test_drawing_keeps_the_turn_and_offers_the_drawn_card(self) -> None:
        after = require(UnoEngine.apply_action(self.game, ONE, draw()))
        self.assertEqual(after.participant_to_act, ONE)
        self.assertEqual(after.drawn_card, number(CARD_COLOR_RED, 2))
        self.assertEqual(cards_held(after, ONE), 2)
        self.assertTrue(UnoEngine.may_pass(after, ONE))
        self.assertFalse(UnoEngine.may_draw(after, ONE))

    def test_the_drawn_card_may_be_played_and_nothing_else(self) -> None:
        drawn = require(UnoEngine.apply_action(self.game, ONE, draw()))
        self.assertIsNone(UnoEngine.apply_action(drawn, ONE, play(number(CARD_COLOR_BLUE, 9))))
        after = require(UnoEngine.apply_action(drawn, ONE, play(number(CARD_COLOR_RED, 2))))
        self.assertEqual(after.participant_to_act, TWO)
        self.assertFalse(after.HasField("drawn_card"))

    def test_passing_after_a_draw_passes_the_turn(self) -> None:
        drawn = require(UnoEngine.apply_action(self.game, ONE, draw()))
        after = require(UnoEngine.apply_action(drawn, ONE, pass_turn()))
        self.assertEqual(after.participant_to_act, TWO)
        self.assertFalse(after.HasField("drawn_card"))

    def test_passing_without_a_draw_is_refused(self) -> None:
        self.assertIsNone(UnoEngine.apply_action(self.game, ONE, pass_turn()))

    def test_drawing_twice_is_refused(self) -> None:
        drawn = require(UnoEngine.apply_action(self.game, ONE, draw()))
        self.assertIsNone(UnoEngine.apply_action(drawn, ONE, draw()))

    def test_an_empty_draw_pile_is_refilled_from_the_discards(self) -> None:
        game = GameBuilder.build(
            hands={ONE: (number(CARD_COLOR_BLUE, 9),), TWO: (number(CARD_COLOR_GREEN, 1),)},
            draw_pile=(),
            top=number(CARD_COLOR_RED, 7),
            active_color=CARD_COLOR_RED,
            participant_to_act=ONE,
        )
        game.discard_pile.insert(0, number(CARD_COLOR_GREEN, 3))
        game.discard_pile.insert(0, number(CARD_COLOR_GREEN, 5))
        after = require(UnoEngine.apply_action(game, ONE, draw()))
        self.assertEqual(list(after.discard_pile), [number(CARD_COLOR_RED, 7)])
        self.assertEqual(len(after.draw_pile), 1)
        self.assertEqual(cards_held(after, ONE), 2)
        self.assertEqual(after.shuffle_count, game.shuffle_count + 1)

    def test_with_nothing_to_draw_the_turn_passes(self) -> None:
        game = GameBuilder.build(
            hands={ONE: (number(CARD_COLOR_BLUE, 9),), TWO: (number(CARD_COLOR_GREEN, 1),)},
            draw_pile=(),
            top=number(CARD_COLOR_RED, 7),
            active_color=CARD_COLOR_RED,
            participant_to_act=ONE,
        )
        after = require(UnoEngine.apply_action(game, ONE, draw()))
        self.assertEqual(after.participant_to_act, TWO)
        self.assertFalse(after.HasField("drawn_card"))


class TwoPlayerTest(unittest.TestCase):
    def test_a_reverse_acts_as_a_skip(self) -> None:
        game = GameBuilder.build(
            hands={
                ONE: (reverse(CARD_COLOR_RED), number(CARD_COLOR_RED, 1)),
                TWO: (number(CARD_COLOR_GREEN, 1),),
            },
            draw_pile=(),
            top=number(CARD_COLOR_RED, 7),
            active_color=CARD_COLOR_RED,
            participant_to_act=ONE,
        )
        after = require(UnoEngine.apply_action(game, ONE, play(reverse(CARD_COLOR_RED))))
        self.assertEqual(after.participant_to_act, ONE)


class EndingTest(unittest.TestCase):
    def test_emptying_the_hand_wins(self) -> None:
        game = GameBuilder.build(
            hands={
                ONE: (number(CARD_COLOR_RED, 5),),
                TWO: (number(CARD_COLOR_GREEN, 1),),
                THREE: (number(CARD_COLOR_YELLOW, 1),),
            },
            draw_pile=(),
            top=number(CARD_COLOR_RED, 7),
            active_color=CARD_COLOR_RED,
            participant_to_act=ONE,
        )
        after = require(UnoEngine.apply_action(game, ONE, play(number(CARD_COLOR_RED, 5))))
        self.assertEqual(after.result.winner, ONE)
        self.assertEqual(after.result.reason, UNO_RESULT_REASON_HAND_EMPTIED)
        self.assertEqual(after.participant_to_act, NOBODY)
        self.assertIsNone(UnoEngine.apply_action(after, TWO, draw()))

    def test_a_last_draw_two_still_makes_the_next_player_draw(self) -> None:
        game = GameBuilder.build(
            hands={
                ONE: (draw_two(CARD_COLOR_RED),),
                TWO: (number(CARD_COLOR_GREEN, 1),),
                THREE: (number(CARD_COLOR_YELLOW, 1),),
            },
            draw_pile=(number(CARD_COLOR_GREEN, 3), number(CARD_COLOR_GREEN, 4)),
            top=number(CARD_COLOR_RED, 7),
            active_color=CARD_COLOR_RED,
            participant_to_act=ONE,
        )
        after = require(UnoEngine.apply_action(game, ONE, play(draw_two(CARD_COLOR_RED))))
        self.assertEqual(after.result.winner, ONE)
        self.assertEqual(cards_held(after, TWO), 3)


class WithdrawTest(unittest.TestCase):
    def setUp(self) -> None:
        self.game = GameBuilder.build(
            hands={
                ONE: (number(CARD_COLOR_RED, 5),),
                TWO: (number(CARD_COLOR_GREEN, 1), number(CARD_COLOR_GREEN, 2)),
                THREE: (number(CARD_COLOR_YELLOW, 7),),
            },
            draw_pile=(number(CARD_COLOR_GREEN, 3),),
            top=number(CARD_COLOR_RED, 7),
            active_color=CARD_COLOR_RED,
            participant_to_act=TWO,
        )

    def test_the_leaver_is_passed_over_and_their_cards_go_under_the_pile(self) -> None:
        after = require(UnoEngine.withdraw(self.game, TWO))
        self.assertEqual(after.participant_to_act, THREE)
        self.assertEqual(cards_held(after, TWO), 0)
        self.assertTrue(after.hands[1].has_withdrawn)
        self.assertEqual(len(after.draw_pile), 3)
        self.assertFalse(after.HasField("result"))
        following = require(
            UnoEngine.apply_action(after, THREE, play(number(CARD_COLOR_YELLOW, 7)))
        )
        self.assertEqual(following.result.winner, THREE)

    def test_leaving_out_of_turn_leaves_the_turn_where_it_was(self) -> None:
        after = require(UnoEngine.withdraw(self.game, ONE))
        self.assertEqual(after.participant_to_act, TWO)
        then = require(UnoEngine.apply_action(after, TWO, draw()))
        then = require(UnoEngine.apply_action(then, TWO, pass_turn()))
        self.assertEqual(then.participant_to_act, THREE)
        then = require(UnoEngine.apply_action(then, THREE, draw()))
        then = require(UnoEngine.apply_action(then, THREE, pass_turn()))
        self.assertEqual(then.participant_to_act, TWO)

    def test_the_last_player_standing_wins(self) -> None:
        after = require(UnoEngine.withdraw(self.game, ONE))
        after = require(UnoEngine.withdraw(after, TWO))
        self.assertEqual(after.result.winner, THREE)
        self.assertEqual(after.result.reason, UNO_RESULT_REASON_OTHERS_WITHDREW)
        self.assertEqual(after.participant_to_act, NOBODY)

    def test_someone_not_in_the_game_cannot_withdraw(self) -> None:
        self.assertIsNone(UnoEngine.withdraw(self.game, ONLOOKER))
        gone = require(UnoEngine.withdraw(self.game, ONE))
        self.assertIsNone(UnoEngine.withdraw(gone, ONE))


class ViewTest(unittest.TestCase):
    def setUp(self) -> None:
        self.game = GameBuilder.build(
            hands={
                ONE: (number(CARD_COLOR_RED, 5), number(CARD_COLOR_BLUE, 9)),
                TWO: (number(CARD_COLOR_GREEN, 1),),
                THREE: (number(CARD_COLOR_YELLOW, 1),),
            },
            draw_pile=(number(CARD_COLOR_GREEN, 3),),
            top=number(CARD_COLOR_RED, 7),
            active_color=CARD_COLOR_RED,
            participant_to_act=ONE,
        )

    def test_a_player_sees_their_own_hand_and_what_may_be_played(self) -> None:
        view = ViewProjector.project(self.game, ONE)
        self.assertEqual(
            [shown.card for shown in view.hand],
            [number(CARD_COLOR_RED, 5), number(CARD_COLOR_BLUE, 9)],
        )
        self.assertEqual([shown.is_playable for shown in view.hand], [True, False])
        self.assertTrue(view.may_draw)
        self.assertFalse(view.may_pass)
        self.assertEqual(view.top_card, number(CARD_COLOR_RED, 7))
        self.assertEqual(view.draw_pile_count, 1)
        self.assertEqual([player.card_count for player in view.players], [2, 1, 1])

    def test_a_player_out_of_turn_may_do_nothing(self) -> None:
        view = ViewProjector.project(self.game, TWO)
        self.assertEqual([shown.is_playable for shown in view.hand], [False])
        self.assertFalse(view.may_draw)
        self.assertFalse(view.may_pass)

    def test_a_spectator_sees_no_hand(self) -> None:
        view = ViewProjector.project(self.game, ONLOOKER)
        self.assertEqual(len(view.hand), 0)
        self.assertFalse(view.may_draw)
        self.assertEqual([player.participant for player in view.players], [ONE, TWO, THREE])
