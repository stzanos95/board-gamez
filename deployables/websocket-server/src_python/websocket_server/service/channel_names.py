"""
The channel each route watches.

The names are the publisher's: an event about a table is published on that
table's channel, and the events the lobby list needs are published on the
lobby's as well.
"""

LOBBY_CHANNEL = "lobby"
TABLE_CHANNEL_PREFIX = "table:"


class ChannelNames:
    """
    The channel a table's events travel on.
    """

    @staticmethod
    def get_table_channel(table_id: str) -> str:
        return f"{TABLE_CHANNEL_PREFIX}{table_id}"
