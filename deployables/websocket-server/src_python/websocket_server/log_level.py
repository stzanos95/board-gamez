import logging
from enum import StrEnum


class LogLevel(StrEnum):
    """
    How much the server writes to its log.
    """

    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"

    @property
    def as_logging_level(self) -> int:
        """
        The number the logging module knows this level by.
        """
        return logging.getLevelNamesMapping()[self.upper()]
