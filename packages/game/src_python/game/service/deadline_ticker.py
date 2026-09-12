"""
The clock tick that hands a run-out state back to its rules.

A tick is a request with no sender: it arrives on an interval and asks the
session controller to expire whatever is due. Nothing is decided here.
"""

import asyncio

from game.controller.session_controller import SessionController


class DeadlineTicker:
    """
    Asks the session controller for run-out states, once per interval, until
    told to stop.

    Built once at the entry point beside the server, and run as a task on the
    same event loop.
    """

    def __init__(self, sessions: SessionController, interval_seconds: float) -> None:
        self._sessions = sessions
        self._interval_seconds = interval_seconds

    async def run(self, stopping: asyncio.Event) -> None:
        """
        Tick until `stopping` is set. A tick in progress finishes before the
        run returns.
        """
        while not stopping.is_set():
            await self._sessions.expire_due_deadlines()
            await DeadlineTicker._wait_for_next_tick(stopping, self._interval_seconds)

    @staticmethod
    async def _wait_for_next_tick(stopping: asyncio.Event, interval_seconds: float) -> None:
        """
        Sleep for the interval, or less if told to stop meanwhile.
        """
        try:
            await asyncio.wait_for(stopping.wait(), timeout=interval_seconds)
        except TimeoutError:
            return
