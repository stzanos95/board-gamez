import unittest

from google.protobuf.wrappers_pb2 import StringValue
from idl.game.dto.rules_pb2 import (
    ApplyActionRequest,
    CreateGameRequest,
    ReadBoundsRequest,
    ReadViewRequest,
)
from idl.game.model.action_pb2 import Action
from idl.game.model.game_type_pb2 import GameType
from idl.game.model.participant_pb2 import ParticipantRole

from game.controller.rules_controller import RulesController
from game.controller.rules_registry import RulesRegistry
from game.service.grpc_rules_service import GrpcRulesService
from tests_python.scripted_rules import MOVE, ScriptedRules

HOSTED = GameType.GAME_TYPE_CHESS
ALSO_HOSTED = GameType.GAME_TYPE_UNO
NOT_HOSTED = GameType.GAME_TYPE_UNSPECIFIED
SEED = 3
FIRST = 1
SECOND = 2
TWO_SEATED = (ParticipantRole(participant=FIRST), ParticipantRole(participant=SECOND))
SMALL_MAXIMUM = 2
LARGE_MAXIMUM = 4


def move_action(participant: int) -> Action:
    action = Action(participant=participant)
    action.payload.Pack(StringValue(value=MOVE))
    return action


class RulesControllerTest(unittest.IsolatedAsyncioTestCase):
    """
    One RulesService for every hosted game, routed by the game type each
    request names.
    """

    def setUp(self) -> None:
        self.small = ScriptedRules(minimum=SMALL_MAXIMUM, maximum=SMALL_MAXIMUM)
        self.large = ScriptedRules(minimum=SMALL_MAXIMUM, maximum=LARGE_MAXIMUM)
        self.controller = RulesController(
            RulesRegistry({HOSTED: self.small, ALSO_HOSTED: self.large})
        )

    async def test_each_game_type_reaches_its_own_rules(self) -> None:
        small = await self.controller.read_bounds(HOSTED)
        large = await self.controller.read_bounds(ALSO_HOSTED)
        assert small is not None and large is not None
        self.assertEqual(small.maximum, SMALL_MAXIMUM)
        self.assertEqual(large.maximum, LARGE_MAXIMUM)
        await self.controller.create_game(ALSO_HOSTED, TWO_SEATED, SEED)
        self.assertEqual(self.large.seeds_received, [SEED])
        self.assertEqual(self.small.seeds_received, [])

    async def test_a_game_not_hosted_answers_nothing(self) -> None:
        self.assertIsNone(await self.controller.read_bounds(NOT_HOSTED))
        self.assertIsNone(await self.controller.create_game(NOT_HOSTED, TWO_SEATED, SEED))
        state = await self.controller.create_game(HOSTED, TWO_SEATED, SEED)
        assert state is not None
        self.assertIsNone(await self.controller.apply_action(NOT_HOSTED, state, move_action(FIRST)))
        self.assertIsNone(await self.controller.read_view(NOT_HOSTED, state, FIRST))
        self.assertIsNone(await self.controller.withdraw_participant(NOT_HOSTED, state, FIRST))
        self.assertIsNone(await self.controller.expire_deadline(NOT_HOSTED, state))

    async def test_the_servicer_routes_by_the_game_type_on_the_request(self) -> None:
        service = GrpcRulesService(self.controller)
        created = await service.CreateGame(
            CreateGameRequest(game_type=HOSTED, participant_roles=TWO_SEATED, seed=SEED),
            context=None,  # type: ignore[arg-type]
        )
        self.assertTrue(created.HasField("state"))
        applied = await service.ApplyAction(
            ApplyActionRequest(game_type=HOSTED, state=created.state, action=move_action(FIRST)),
            context=None,  # type: ignore[arg-type]
        )
        self.assertEqual(list(applied.state.participants_to_act), [SECOND])
        view = await service.ReadView(
            ReadViewRequest(game_type=HOSTED, state=created.state, participant=FIRST),
            context=None,  # type: ignore[arg-type]
        )
        self.assertTrue(view.HasField("view"))
        unhosted = await service.ReadBounds(
            ReadBoundsRequest(game_type=NOT_HOSTED),
            context=None,  # type: ignore[arg-type]
        )
        self.assertFalse(unhosted.HasField("bounds"))
