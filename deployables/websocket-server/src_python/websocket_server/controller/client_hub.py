"""
Who is connected, and what each connection watches.
"""

from websocket_server.controller.base_client import BaseClient

ClientsByChannel = dict[str, set[BaseClient]]


class ClientHub:
    """
    Every open connection, grouped by the channel it watches.

    Bookkeeping only. It does not subscribe, and it does not decide what to
    send; it holds the clients and hands a frame to each one watching a
    channel.
    """

    def __init__(self) -> None:
        self._clients: ClientsByChannel = {}

    def attach(self, channel: str, client: BaseClient) -> None:
        """
        Start sending this client what is broadcast on this channel.
        """
        self._clients.setdefault(channel, set()).add(client)

    def detach(self, channel: str, client: BaseClient) -> None:
        """
        Stop sending this client what is broadcast on this channel. A client
        that was not watching it is left alone.
        """
        watchers = self._clients.get(channel)
        if watchers is None:
            return
        watchers.discard(client)
        if not watchers:
            del self._clients[channel]

    def get_watcher_count(self, channel: str) -> int:
        """
        How many clients watch this channel.
        """
        return len(self._clients.get(channel, ()))

    def get_watched_channels(self) -> frozenset[str]:
        """
        Every channel at least one client watches.
        """
        return frozenset(self._clients)

    def broadcast(self, channel: str, frame: bytes) -> None:
        """
        Send this frame to every client watching this channel.
        """
        for client in tuple(self._clients.get(channel, ())):
            client.send(frame)
