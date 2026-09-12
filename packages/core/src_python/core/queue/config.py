"""
Which broker carries messages, and the settings each option needs.

An enum selects, one config dataclass describes each option, and the container
carries one optional field per option. The enum and the configs share a module
because they form one contract.

Adding a broker means adding a member, a config, a field on QueueConfig, a
directory holding its publisher and consumer, and two registry entries in
`provider`. Nothing existing changes.
"""

from dataclasses import dataclass
from enum import StrEnum

from mashumaro.mixins.yaml import DataClassYAMLMixin


class QueueType(StrEnum):
    """
    Which broker to build.

    A member here is a broker this system may be configured for. One with no
    entry in the provider's registries is refused at bringup.
    """

    REDIS = "redis"
    KAFKA = "kafka"


@dataclass(frozen=True, slots=True)
class RedisQueueConfig(DataClassYAMLMixin):
    """
    The Redis instance messages pass through, and the channels they pass on.

    `channel_prefix` begins every channel this queue publishes to or subscribes
    on, so one instance can carry more than one deployment.
    """

    host: str
    port: int
    database: int
    channel_prefix: str


@dataclass(frozen=True, slots=True)
class KafkaQueueConfig(DataClassYAMLMixin):
    """
    The Kafka cluster messages pass through.
    """

    bootstrap_servers: str


@dataclass(frozen=True, slots=True)
class QueueConfig(DataClassYAMLMixin):
    """
    The chosen broker, and the settings for each broker that has any.

    One optional field per broker type. The selected one must be present; the
    rest are ignored, so a file may carry settings for a broker it is not using.
    """

    queue: QueueType
    redis_config: RedisQueueConfig | None = None
    kafka_config: KafkaQueueConfig | None = None
