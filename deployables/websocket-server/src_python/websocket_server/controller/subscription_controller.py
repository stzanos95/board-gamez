"""
Which channels are subscribed, and what arriving on one becomes.
"""

import asyncio
import logging
from collections.abc import Sequence

from core.protobuf.message_utils import ProtobufMessageUtils
from core.queue.base_queue_consumer import BaseQueueConsumer
from core.queue.received_message import ReceivedMessage

from websocket_server.adapters.event_adapters import EventAdapters
from websocket_server.controller.base_client import BaseClient
from websocket_server.controller.client_hub import ClientHub

FIRST_WATCHER_COUNT = 1
NO_WATCHER_COUNT = 0


class SubscriptionController:
    """
    The one place that decides what a connection is sent.

    A channel is subscribed on every source while at least one client watches
    it, and unsubscribed when the last one leaves. Every message a source
    yields becomes one frame, sent to every client watching the channel it
    arrived on; a message of a type this build does not know is dropped.

    Built once at the entry point. `start` begins the relays on the running
    event loop, and `close` ends them.
    """

    def __init__(self, hub: ClientHub, sources: Sequence[BaseQueueConsumer]) -> None:
        self._hub = hub
        self._sources = tuple(sources)
        self._relays: list[asyncio.Task[None]] = []
        self._log = logging.getLogger(SubscriptionController.__name__)

    async def attach(self, channel: str, client: BaseClient) -> None:
        """
        Start sending this client what happens on this channel.

        The client is held before any source is asked, so a connection that
        closes while the subscription is being made is still let go of.
        """
        self._hub.attach(channel, client)
        if self._hub.get_watcher_count(channel) == FIRST_WATCHER_COUNT:
            for source in self._sources:
                await source.subscribe(channel)

    async def detach(self, channel: str, client: BaseClient) -> None:
        """
        Stop sending this client what happens on this channel.
        """
        self._hub.detach(channel, client)
        if self._hub.get_watcher_count(channel) == NO_WATCHER_COUNT:
            for source in self._sources:
                await source.unsubscribe(channel)

    async def start(self) -> None:
        """
        Begin relaying every source, on the running event loop.
        """
        loop = asyncio.get_running_loop()
        self._relays = [loop.create_task(self._relay(source)) for source in self._sources]

    async def close(self) -> None:
        """
        Stop relaying and release every source.
        """
        for relay in self._relays:
            relay.cancel()
        await asyncio.gather(*self._relays, return_exceptions=True)
        self._relays = []
        for source in self._sources:
            await source.close()

    def relay(self, received: ReceivedMessage) -> None:
        """
        Send what this message became to every client watching the channel it
        arrived on.
        """
        frame = EventAdapters.envelope_to_frame(received.envelope)
        if frame is None:
            self._log.debug("dropped a %s on %s", received.envelope.header.type, received.channel)
            return
        self._hub.broadcast(received.channel, ProtobufMessageUtils.message_to_bytes(frame))

    async def _relay(self, source: BaseQueueConsumer) -> None:
        async for received in source.messages():
            self.relay(received)
