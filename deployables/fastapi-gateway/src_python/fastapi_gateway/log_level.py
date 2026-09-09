from enum import StrEnum


class LogLevel(StrEnum):
    """
    How much the server writes to its log, in the spelling uvicorn expects.
    """

    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"
    TRACE = "trace"
