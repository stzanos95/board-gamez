import unittest

from core.queue.config import KafkaQueueConfig, QueueConfig, QueueType, RedisQueueConfig
from core.queue.provider import QueueProvider
from core.queue.redis.consumer import RedisQueueConsumer
from core.queue.redis.publisher import RedisQueuePublisher

REDIS_CONFIG = RedisQueueConfig(host="localhost", port=6379, database=0, channel_prefix="test")
KAFKA_CONFIG = KafkaQueueConfig(bootstrap_servers="localhost:9092")


class QueueProviderTest(unittest.TestCase):
    """
    Which publisher and consumer the configuration selects, and what is
    refused at bringup.
    """

    def test_redis_builds_a_redis_publisher_and_consumer(self) -> None:
        config = QueueConfig(queue=QueueType.REDIS, redis_config=REDIS_CONFIG)
        self.assertIsInstance(QueueProvider.get_publisher(config), RedisQueuePublisher)
        self.assertIsInstance(QueueProvider.get_consumer(config), RedisQueueConsumer)

    def test_redis_without_its_settings_is_refused(self) -> None:
        config = QueueConfig(queue=QueueType.REDIS)
        with self.assertRaisesRegex(ValueError, "redis_config is missing"):
            QueueProvider.get_publisher(config)
        with self.assertRaisesRegex(ValueError, "redis_config is missing"):
            QueueProvider.get_consumer(config)

    def test_a_broker_nothing_implements_is_refused(self) -> None:
        config = QueueConfig(queue=QueueType.KAFKA, kafka_config=KAFKA_CONFIG)
        with self.assertRaisesRegex(ValueError, "no queue publisher is registered for 'kafka'"):
            QueueProvider.get_publisher(config)
        with self.assertRaisesRegex(ValueError, "no queue consumer is registered for 'kafka'"):
            QueueProvider.get_consumer(config)

    def test_settings_for_an_unselected_broker_are_ignored(self) -> None:
        config = QueueConfig(
            queue=QueueType.REDIS, redis_config=REDIS_CONFIG, kafka_config=KAFKA_CONFIG
        )
        self.assertIsInstance(QueueProvider.get_publisher(config), RedisQueuePublisher)

    def test_the_config_reads_from_yaml(self) -> None:
        config = QueueConfig.from_yaml(
            "queue: redis\n"
            "redis_config:\n"
            "  host: broker\n"
            "  port: 6379\n"
            "  database: 2\n"
            "  channel_prefix: gamez\n"
        )
        self.assertIs(config.queue, QueueType.REDIS)
        self.assertEqual(config.redis_config, RedisQueueConfig("broker", 6379, 2, "gamez"))
        self.assertIsNone(config.kafka_config)
