"""
Which store holds tables, and the settings each option needs.

An enum selects, one config dataclass describes each option, and the container
carries one optional field per option. The enum and the configs share a module
because they form one contract.

Adding a store means adding a member, a config, a field on TableRepositoryConfig,
a class and a registry entry in `provider`. Nothing existing changes.
"""

from dataclasses import dataclass
from enum import StrEnum

from mashumaro.mixins.yaml import DataClassYAMLMixin


class TableRepositoryType(StrEnum):
    """
    Which store to build.
    """

    REDIS = "redis"


@dataclass(frozen=True, slots=True)
class RedisTableRepositoryConfig(DataClassYAMLMixin):
    """
    The Redis instance tables are kept in, and the keys they are kept under.

    `key_prefix` begins every key this repository writes, so one instance can
    hold more than one deployment.
    """

    host: str
    port: int
    database: int
    key_prefix: str


@dataclass(frozen=True, slots=True)
class TableRepositoryConfig(DataClassYAMLMixin):
    """
    The chosen store, and the settings for each store that has any.

    One optional field per store type. The selected one must be present; the
    rest are ignored, so a file may carry settings for a store it is not using.
    """

    repository: TableRepositoryType
    redis_config: RedisTableRepositoryConfig | None = None
