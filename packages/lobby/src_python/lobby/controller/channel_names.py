"""
The channels the lobby publishes on.

Every event about a table is published on that table's channel. The events a
listing of tables needs are published on the lobby's channel as well.
"""

LOBBY_CHANNEL = "lobby"
TABLE_CHANNEL_PREFIX = "table:"


class LobbyChannelNames:
    """
    The channel a table's events travel on.
    """

    @staticmethod
    def get_table_channel(table_id: str) -> str:
        return f"{TABLE_CHANNEL_PREFIX}{table_id}"
