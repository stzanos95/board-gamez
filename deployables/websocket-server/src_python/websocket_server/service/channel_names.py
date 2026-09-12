"""
The channels each route watches.

The names are the publishers': the lobby publishes a table's events on
`table:<id>` and the events its listing needs on `lobby`; the platform
publishes a game's events on `session:<id>`. A game is played at the table
whose id it carries, so a table's socket watches both of that id's channels.
"""

LOBBY_CHANNEL = "lobby"
TABLE_CHANNEL_PREFIX = "table:"
SESSION_CHANNEL_PREFIX = "session:"


class ChannelNames:
    """
    The channels a socket on a table watches.
    """

    @staticmethod
    def get_table_channels(table_id: str) -> tuple[str, ...]:
        return (f"{TABLE_CHANNEL_PREFIX}{table_id}", f"{SESSION_CHANNEL_PREFIX}{table_id}")
