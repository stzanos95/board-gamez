"""
The channels the platform publishes on.

Every event about a game is published on that game's channel.
"""

SESSION_CHANNEL_PREFIX = "session:"


class GameChannelNames:
    """
    The channel a game's events travel on.
    """

    @staticmethod
    def get_session_channel(session_id: str) -> str:
        return f"{SESSION_CHANNEL_PREFIX}{session_id}"
