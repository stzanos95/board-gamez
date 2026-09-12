"""
How a channel name and a deployment's prefix are joined.
"""

CHANNEL_SEPARATOR = ":"


class RedisChannelNames:
    """
    The channel a message travels on, under the prefix a deployment keeps its
    channels under.
    """

    @staticmethod
    def get_prefixed(prefix: str, channel: str) -> str:
        return f"{prefix}{CHANNEL_SEPARATOR}{channel}"
