"""
How a channel name and a deployment's prefix are joined, and taken apart.
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

    @staticmethod
    def get_unprefixed(prefix: str, prefixed: str) -> str | None:
        """
        The channel name under this prefix, or None when the name is not under
        it.
        """
        head = f"{prefix}{CHANNEL_SEPARATOR}"
        if not prefixed.startswith(head):
            return None
        return prefixed[len(head) :]
