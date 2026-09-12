"""
The time as this machine keeps it.
"""

from datetime import UTC, datetime

from core.clock.base_clock import BaseClock


class SystemClock(BaseClock):
    """
    The current time, read from the system.
    """

    def now(self) -> datetime:
        return datetime.now(UTC)
