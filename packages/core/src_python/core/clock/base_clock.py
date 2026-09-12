"""
What any source of the current time answers.
"""

from abc import ABC, abstractmethod
from datetime import datetime


class BaseClock(ABC):
    """
    Where the current time comes from, whatever keeps it.

    A component that stamps a time holds one of these, so a test can hold the
    time still.
    """

    @abstractmethod
    def now(self) -> datetime:
        """
        The current instant, timezone-aware and in UTC.
        """
