import unittest

from google.protobuf.wrappers_pb2 import StringValue
from idl.chess.model import game_pb2, piece_pb2
from idl.game.model.action_pb2 import Action
from idl.game.model.game_result_pb2 import ParticipantOutcome
from idl.game.model.game_state_pb2 import GameState
from idl.game.model.participant_pb2 import ParticipantRole

from product_chess.adapters.chess_rules_adapters import ChessRulesAdapters
from product_chess.adapters.chess_seat_adapters import ChessSeatAdapters
from product_chess.controller.chess_rules import ChessRules
from tests_python.chess_actions import move_action, packed, resignation_action

NOBODY = 0
WHITE_PARTICIPANT = 1
BLACK_PARTICIPANT = 2
ONLOOKER = 3


def seated_as(participant: int, color: piece_pb2.Color) -> ParticipantRole:
    return ParticipantRole(participant=participant, role=ChessSeatAdapters.color_to_role(color))


WHITE_SEATED = seated_as(WHITE_PARTICIPANT, piece_pb2.COLOR_WHITE)
BLACK_SEATED = seated_as(BLACK_PARTICIPANT, piece_pb2.COLOR_BLACK)
SCHOLARS_MATE = ("e2e4", "e7e5", "f1c4", "b8c6", "d1h5", "g8f6", "h5f7")
KNIGHT_SHUFFLE = ("g1f3", "g8f6", "f3g1", "f6g8")


def require_state(state: GameState | None) -> GameState:
    assert state is not None
    return state


def require_game(state: GameState) -> game_pb2.ChessGame:
    game = ChessRulesAdapters.game_state_to_chess_game(state)
    assert game is not None
    return game


class ChessRulesTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.rules = ChessRules()

    async def new_game(self) -> GameState:
        return require_state(await self.rules.create_game((WHITE_SEATED, BLACK_SEATED)))

    async def play_all(self, state: GameState, texts: tuple[str, ...]) -> GameState:
        for text in texts:
            state = require_state(
                await self.rules.apply_action(state, move_action(state.participant_to_act, text))
            )
        return state

    async def test_a_game_takes_exactly_two(self) -> None:
        self.assertIsNone(await self.rules.create_game((WHITE_SEATED,)))
        self.assertIsNone(
            await self.rules.create_game(
                (WHITE_SEATED, BLACK_SEATED, seated_as(ONLOOKER, piece_pb2.COLOR_WHITE))
            )
        )
        self.assertIsNotNone(await self.rules.create_game((WHITE_SEATED, BLACK_SEATED)))

    async def test_a_game_takes_one_of_each_side(self) -> None:
        both_white = (WHITE_SEATED, seated_as(BLACK_PARTICIPANT, piece_pb2.COLOR_WHITE))
        self.assertIsNone(await self.rules.create_game(both_white))
        unseated = (WHITE_SEATED, ParticipantRole(participant=BLACK_PARTICIPANT))
        self.assertIsNone(await self.rules.create_game(unseated))

    async def test_the_side_comes_from_the_role_and_not_the_number(self) -> None:
        swapped = (
            seated_as(WHITE_PARTICIPANT, piece_pb2.COLOR_BLACK),
            seated_as(BLACK_PARTICIPANT, piece_pb2.COLOR_WHITE),
        )
        game = require_game(require_state(await self.rules.create_game(swapped)))
        self.assertEqual(game.roster.white.participant, BLACK_PARTICIPANT)
        self.assertEqual(game.roster.black.participant, WHITE_PARTICIPANT)

    async def test_the_bounds_say_two(self) -> None:
        bounds = await self.rules.read_bounds()
        self.assertEqual((bounds.minimum, bounds.maximum), (2, 2))

    async def test_a_new_game_has_white_to_act_and_no_result(self) -> None:
        state = await self.new_game()
        self.assertEqual(state.participant_to_act, WHITE_PARTICIPANT)
        self.assertFalse(state.HasField("result"))
        game = require_game(state)
        self.assertEqual(game.roster.white.participant, WHITE_PARTICIPANT)
        self.assertEqual(game.roster.black.participant, BLACK_PARTICIPANT)
        self.assertEqual(len(game.legal_moves), 20)

    async def test_a_legal_move_passes_the_turn(self) -> None:
        state = await self.new_game()
        after = require_state(
            await self.rules.apply_action(state, move_action(WHITE_PARTICIPANT, "e2e4"))
        )
        self.assertEqual(after.participant_to_act, BLACK_PARTICIPANT)
        self.assertEqual(require_game(after).history.turns[0].notation, "e4")
        # The state handed in is untouched: the rules answer a new one.
        self.assertEqual(state.participant_to_act, WHITE_PARTICIPANT)

    async def test_participant_to_act_alternates_ply_by_ply(self) -> None:
        state = await self.new_game()
        expected = (BLACK_PARTICIPANT, WHITE_PARTICIPANT, BLACK_PARTICIPANT, WHITE_PARTICIPANT)
        for text, participant in zip(KNIGHT_SHUFFLE, expected, strict=True):
            state = await self.play_all(state, (text,))
            self.assertEqual(state.participant_to_act, participant)

    async def test_an_illegal_move_is_refused(self) -> None:
        state = await self.new_game()
        self.assertIsNone(
            await self.rules.apply_action(state, move_action(WHITE_PARTICIPANT, "e2e5"))
        )

    async def test_the_wrong_participant_is_refused(self) -> None:
        state = await self.new_game()
        self.assertIsNone(
            await self.rules.apply_action(state, move_action(BLACK_PARTICIPANT, "e7e5"))
        )
        self.assertIsNone(await self.rules.apply_action(state, move_action(ONLOOKER, "e2e4")))

    async def test_a_payload_that_is_not_a_chess_action_is_refused(self) -> None:
        state = await self.new_game()
        stray = Action(participant=WHITE_PARTICIPANT)
        stray.payload.Pack(StringValue(value="e2e4"))
        self.assertIsNone(await self.rules.apply_action(state, stray))

    async def test_a_state_that_is_not_a_chess_game_is_refused(self) -> None:
        stray = GameState(participant_to_act=WHITE_PARTICIPANT)
        stray.payload.Pack(StringValue(value="not chess"))
        self.assertIsNone(
            await self.rules.apply_action(stray, move_action(WHITE_PARTICIPANT, "e2e4"))
        )

    async def test_resigning_ends_the_game_with_the_other_side_winning(self) -> None:
        state = await self.play_all(await self.new_game(), ("e2e4",))
        after = require_state(
            await self.rules.apply_action(state, resignation_action(BLACK_PARTICIPANT))
        )
        self.assertEqual(after.participant_to_act, NOBODY)
        outcomes = {item.participant: item.outcome for item in after.result.participant_items}
        self.assertEqual(outcomes[WHITE_PARTICIPANT], ParticipantOutcome.PARTICIPANT_OUTCOME_WON)
        self.assertEqual(outcomes[BLACK_PARTICIPANT], ParticipantOutcome.PARTICIPANT_OUTCOME_LOST)
        self.assertEqual(require_game(after).resigning_color, piece_pb2.COLOR_BLACK)

    async def test_mate_scores_the_winner_and_the_loser(self) -> None:
        state = await self.play_all(await self.new_game(), SCHOLARS_MATE)
        self.assertEqual(state.participant_to_act, NOBODY)
        outcomes = {item.participant: item.outcome for item in state.result.participant_items}
        self.assertEqual(outcomes[WHITE_PARTICIPANT], ParticipantOutcome.PARTICIPANT_OUTCOME_WON)
        self.assertEqual(outcomes[BLACK_PARTICIPANT], ParticipantOutcome.PARTICIPANT_OUTCOME_LOST)

    async def test_a_draw_scores_both_sides_as_drawn(self) -> None:
        state = await self.play_all(await self.new_game(), (*KNIGHT_SHUFFLE, *KNIGHT_SHUFFLE))
        self.assertEqual(state.participant_to_act, NOBODY)
        outcomes = {item.participant: item.outcome for item in state.result.participant_items}
        self.assertEqual(set(outcomes.values()), {ParticipantOutcome.PARTICIPANT_OUTCOME_DRAW})

    async def test_nothing_can_be_played_once_the_game_is_over(self) -> None:
        state = await self.play_all(await self.new_game(), SCHOLARS_MATE)
        self.assertIsNone(
            await self.rules.apply_action(state, move_action(BLACK_PARTICIPANT, "e7e6"))
        )
        self.assertIsNone(
            await self.rules.apply_action(state, resignation_action(BLACK_PARTICIPANT))
        )

    async def test_every_viewer_sees_the_whole_game(self) -> None:
        state = await self.play_all(await self.new_game(), ("e2e4",))
        for participant in (WHITE_PARTICIPANT, BLACK_PARTICIPANT, NOBODY):
            with self.subTest(participant=participant):
                view = await self.rules.read_view(state, participant)
                self.assertEqual(view, state.payload)
                self.assertIsNot(view, state.payload)

    async def test_an_action_survives_packing(self) -> None:
        action = move_action(WHITE_PARTICIPANT, "e7e8q")
        unpacked = ChessRulesAdapters.action_to_chess_action(action)
        assert unpacked is not None
        self.assertEqual(unpacked.move.promotion_type, piece_pb2.PIECE_TYPE_QUEEN)
        self.assertEqual(packed(unpacked), action.payload)
