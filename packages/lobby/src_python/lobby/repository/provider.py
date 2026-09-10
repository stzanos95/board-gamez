"""
Building the store the configuration asked for.

A registry rather than a chain of conditionals: a new store is an entry here and
its own module.
"""

from collections.abc import Callable

from lobby.repository.base_table_repository import BaseTableRepository
from lobby.repository.config import TableRepositoryConfig, TableRepositoryType
from lobby.repository.redis_table_repository import RedisTableRepository


class TableRepositoryProvider:
    """
    The one place a table repository is constructed.
    """

    @staticmethod
    def get_table_repository(config: TableRepositoryConfig) -> BaseTableRepository:
        """
        The store the configuration selects, holding its own settings.

        Raises ValueError when the selected store has no builder, or when its
        settings section is missing.
        """
        builder = TABLE_REPOSITORY_BUILDERS_BY_TYPE.get(config.repository)
        if builder is None:
            raise ValueError(
                f"no table repository is registered for {config.repository.value!r}; "
                f"known repositories are "
                f"{', '.join(sorted(TABLE_REPOSITORY_BUILDERS_BY_TYPE))}"
            )
        return builder(config)

    @staticmethod
    def _build_redis_table_repository(config: TableRepositoryConfig) -> BaseTableRepository:
        if config.redis_config is None:
            raise ValueError(
                f"table repository is {TableRepositoryType.REDIS.value!r} but redis_config is "
                f"missing; add a redis_config section to the configuration file"
            )
        return RedisTableRepository(config=config.redis_config)


# Keys are data — a repository type names its builder. This is a lookup, not a
# record. Defined after the class so it can name the static methods above.
TABLE_REPOSITORY_BUILDERS_BY_TYPE: dict[
    TableRepositoryType, Callable[[TableRepositoryConfig], BaseTableRepository]
] = {
    TableRepositoryType.REDIS: TableRepositoryProvider._build_redis_table_repository,
}
