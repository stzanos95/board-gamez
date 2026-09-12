import unittest

from google.protobuf import any_pb2
from idl.game.dto.command_pb2 import ApplyCommandRequest
from idl.game.dto.session_pb2 import CreateSessionRequest, ReadSessionRequest
from idl.game.model.command_result_pb2 import CommandOutcome, CommandResult
from idl.game.model.game_type_pb2 import GameType
from idl.game.model.participant_pb2 import Participant
from idl.game.model.session_pb2 import SessionView

from game.controller.rules_registry import RulesRegistry
from game.controller.session_controller import SessionController
from game.service.grpc_session_service import GrpcSessionService
from tests_python.in_memory_queue_publisher import InMemoryQueuePublisher
from tests_python.in_memory_session_repository import InMemorySessionRepository

SESSION_ID = "t-1"
PLAYER_ID = "p-1"
COMMAND_ID = "c-1"
EXPECTED_VERSION = 4


class RecordingController(SessionController):
    """
    A controller that answers without deciding anything, so what the servicer
    unpacks is what the test can see.
    """

    def __init__(self) -> None:
        super().__init__(
            repository=InMemorySessionRepository(),
            rules=RulesRegistry({}),
            queue_publisher=InMemoryQueuePublisher(),
        )
        self.callers: list[str] = []
        self.created: list[tuple[str, GameType, tuple[Participant, ...]]] = []
        self.read_ids: list[str] = []
        self.commands: list[tuple[str, str, int]] = []

    async def create_session(
        self,
        table_id: str,
        game_type: GameType,
        participants: tuple[Participant, ...],
        player_id: str,
    ) -> SessionView | None:
        self.callers.append(player_id)
        self.created.append((table_id, game_type, participants))
        return SessionView(id=table_id)

    async def read_session(self, session_id: str, player_id: str) -> SessionView | None:
        self.callers.append(player_id)
        self.read_ids.append(session_id)
        return None

    async def apply_command(
        self,
        session_id: str,
        player_id: str,
        command_id: str,
        action: any_pb2.Any,
        expected_version: int,
    ) -> CommandResult:
        self.callers.append(player_id)
        self.commands.append((session_id, command_id, expected_version))
        return CommandResult(outcome=CommandOutcome.COMMAND_OUTCOME_APPLIED)


class UnpackingTest(unittest.IsolatedAsyncioTestCase):
    """
    The servicer decides nothing. It hands the controller the arguments an
    operation takes and packs what comes back into the schema's response.
    """

    async def test_a_create_reaches_the_controller_with_its_player(self) -> None:
        controller = RecordingController()
        service = GrpcSessionService(controller=controller)
        participants = (Participant(number=1, player_id=PLAYER_ID),)

        response = await service.CreateSession(
            CreateSessionRequest(
                table_id=SESSION_ID,
                player_id=PLAYER_ID,
                game_type=GameType.GAME_TYPE_CHESS,
                participants=participants,
            ),
            context=None,  # type: ignore[arg-type]
        )

        self.assertEqual(controller.callers, [PLAYER_ID])
        self.assertEqual(controller.created, [(SESSION_ID, GameType.GAME_TYPE_CHESS, participants)])
        self.assertEqual(response.session.id, SESSION_ID)

    async def test_a_read_reaches_the_controller_with_its_player(self) -> None:
        controller = RecordingController()
        service = GrpcSessionService(controller=controller)

        response = await service.ReadSession(
            ReadSessionRequest(session_id=SESSION_ID, player_id=PLAYER_ID),
            context=None,  # type: ignore[arg-type]
        )

        self.assertEqual(controller.callers, [PLAYER_ID])
        self.assertEqual(controller.read_ids, [SESSION_ID])
        self.assertFalse(response.HasField("session"))

    async def test_a_command_reaches_the_controller_with_its_player(self) -> None:
        controller = RecordingController()
        service = GrpcSessionService(controller=controller)

        response = await service.ApplyCommand(
            ApplyCommandRequest(
                session_id=SESSION_ID,
                command_id=COMMAND_ID,
                player_id=PLAYER_ID,
                expected_version=EXPECTED_VERSION,
            ),
            context=None,  # type: ignore[arg-type]
        )

        self.assertEqual(controller.callers, [PLAYER_ID])
        self.assertEqual(controller.commands, [(SESSION_ID, COMMAND_ID, EXPECTED_VERSION)])
        self.assertEqual(response.result.outcome, CommandOutcome.COMMAND_OUTCOME_APPLIED)
        self.assertFalse(response.result.HasField("session"))

    async def test_a_request_naming_no_player_reaches_the_controller_as_nobody(self) -> None:
        controller = RecordingController()
        service = GrpcSessionService(controller=controller)

        await service.ReadSession(
            ReadSessionRequest(session_id=SESSION_ID),
            context=None,  # type: ignore[arg-type]
        )

        self.assertEqual(controller.callers, [""])
