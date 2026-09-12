import asyncio
import unittest

from idl.game.model.game_type_pb2 import GameType

from game.controller.rules_registry import RulesRegistry
from game.controller.session_controller import SessionController
from game.service.deadline_ticker import DeadlineTicker
from tests_python.fixed_clock import FixedClock
from tests_python.in_memory_queue_publisher import InMemoryQueuePublisher
from tests_python.in_memory_session_repository import InMemorySessionRepository
from tests_python.scripted_rules import ScriptedRules

SHORT_INTERVAL_SECONDS = 0.01
LONG_INTERVAL_SECONDS = 60.0
A_FEW_TICKS = 3


class CountingController(SessionController):
    """
    A session controller that counts how often it is asked to expire.
    """

    def __init__(self) -> None:
        super().__init__(
            repository=InMemorySessionRepository(),
            rules=RulesRegistry({GameType.GAME_TYPE_CHESS: ScriptedRules(minimum=2, maximum=2)}),
            queue_publisher=InMemoryQueuePublisher(),
            clock=FixedClock(),
        )
        self.ticks = 0
        self.ticked = asyncio.Event()

    async def expire_due_deadlines(self) -> None:
        self.ticks += 1
        if self.ticks >= A_FEW_TICKS:
            self.ticked.set()


class DeadlineTickerTest(unittest.IsolatedAsyncioTestCase):
    async def test_the_controller_is_asked_once_per_interval_until_stopped(self) -> None:
        controller = CountingController()
        stopping = asyncio.Event()
        ticker = DeadlineTicker(sessions=controller, interval_seconds=SHORT_INTERVAL_SECONDS)

        running = asyncio.create_task(ticker.run(stopping))
        await controller.ticked.wait()
        stopping.set()
        await running

        self.assertGreaterEqual(controller.ticks, A_FEW_TICKS)

    async def test_stopping_cuts_a_long_interval_short(self) -> None:
        controller = CountingController()
        stopping = asyncio.Event()
        ticker = DeadlineTicker(sessions=controller, interval_seconds=LONG_INTERVAL_SECONDS)

        running = asyncio.create_task(ticker.run(stopping))
        await asyncio.sleep(0)
        stopping.set()
        await asyncio.wait_for(running, timeout=1.0)

        self.assertEqual(controller.ticks, 1)
