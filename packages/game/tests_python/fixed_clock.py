"""
A clock a test sets.
"""

from datetime import UTC, datetime

from core.clock.base_clock import BaseClock

START_OF_TEST = datetime(2026, 1, 1, tzinfo=UTC)


class FixedClock(BaseClock):
    """
    Answers the instant it was last set to, and nothing moves it but the test.
    """

    def __init__(self, instant: datetime = START_OF_TEST) -> None:
        self.instant = instant

    def now(self) -> datetime:
        return self.instant
