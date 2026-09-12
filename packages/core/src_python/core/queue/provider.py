"""
Building the publisher and the consumer the configuration asked for.

A registry rather than a chain of conditionals: a new broker is two entries here
and a directory of its own. A broker type with no entry is refused at bringup,
which is how a type the schema names but nothing implements yet stays out of a
running process.
"""

from collections.abc import Callable
from typing import ClassVar

from core.queue.base_queue_consumer import BaseQueueConsumer
from core.queue.base_queue_publisher import BaseQueuePublisher
from core.queue.config import QueueConfig, QueueType, RedisQueueConfig
from core.queue.redis.consumer import RedisQueueConsumer
from core.queue.redis.publisher import RedisQueuePublisher


class QueueProvider:
    """
    The one place a publisher or a consumer is constructed.
    """

    @staticmethod
    def get_publisher(config: QueueConfig) -> BaseQueuePublisher:
        """
        The publisher the configuration selects, holding its own settings.

        Raises ValueError when the selected broker has no publisher, or when its
        settings section is missing.
        """
        builder = QueueProvider.PUBLISHER_BUILDERS_BY_TYPE.get(config.queue)
        if builder is None:
            raise ValueError(
                f"no queue publisher is registered for {config.queue.value!r}; "
                f"known brokers are {', '.join(sorted(QueueProvider.PUBLISHER_BUILDERS_BY_TYPE))}"
            )
        return builder(config)

    @staticmethod
    def get_consumer(config: QueueConfig) -> BaseQueueConsumer:
        """
        The consumer the configuration selects, holding its own settings.

        Raises ValueError when the selected broker has no consumer, or when its
        settings section is missing.
        """
        builder = QueueProvider.CONSUMER_BUILDERS_BY_TYPE.get(config.queue)
        if builder is None:
            raise ValueError(
                f"no queue consumer is registered for {config.queue.value!r}; "
                f"known brokers are {', '.join(sorted(QueueProvider.CONSUMER_BUILDERS_BY_TYPE))}"
            )
        return builder(config)

    @staticmethod
    def _build_redis_publisher(config: QueueConfig) -> BaseQueuePublisher:
        return RedisQueuePublisher(config=QueueProvider._require_redis_config(config))

    @staticmethod
    def _build_redis_consumer(config: QueueConfig) -> BaseQueueConsumer:
        return RedisQueueConsumer(config=QueueProvider._require_redis_config(config))

    @staticmethod
    def _require_redis_config(config: QueueConfig) -> RedisQueueConfig:
        if config.redis_config is None:
            raise ValueError(
                f"queue is {QueueType.REDIS.value!r} but redis_config is missing; "
                f"add a redis_config section to the configuration file"
            )
        return config.redis_config

    # Keys are data — a broker type names its builder. These are lookups, not
    # records, and they follow the builders they name.
    PUBLISHER_BUILDERS_BY_TYPE: ClassVar[
        dict[QueueType, Callable[[QueueConfig], BaseQueuePublisher]]
    ] = {
        QueueType.REDIS: _build_redis_publisher,
    }

    CONSUMER_BUILDERS_BY_TYPE: ClassVar[
        dict[QueueType, Callable[[QueueConfig], BaseQueueConsumer]]
    ] = {
        QueueType.REDIS: _build_redis_consumer,
    }
