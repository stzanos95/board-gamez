"""
A consumer fed from the test, so a controller test needs no broker.
"""

import asyncio
from collections.abc import AsyncIterator

from core.queue.base_queue_consumer import BaseQueueConsumer
from core.queue.received_message import ReceivedMessage


class InMemoryQueueConsumer(BaseQueueConsumer):
    """
    Records every subscribe and unsubscribe, and yields what `deliver` was
    given until `close` is called.
    """

    def __init__(self) -> None:
        self.subscribed: list[str] = []
        self.unsubscribed: list[str] = []
        self.closed = False
        self._queue: asyncio.Queue[ReceivedMessage | None] = asyncio.Queue()

    async def subscribe(self, channel: str) -> None:
        self.subscribed.append(channel)

    async def unsubscribe(self, channel: str) -> None:
        self.unsubscribed.append(channel)

    async def messages(self) -> AsyncIterator[ReceivedMessage]:
        while True:
            received = await self._queue.get()
            if received is None:
                return
            yield received

    async def close(self) -> None:
        self.closed = True
        await self._queue.put(None)

    async def deliver(self, received: ReceivedMessage) -> None:
        await self._queue.put(received)
