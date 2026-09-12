"""
Building the store the configuration asked for.

A registry rather than a chain of conditionals: a new store is an entry here and
its own module.
"""

from collections.abc import Callable
from typing import ClassVar

from game.repository.base_session_repository import BaseSessionRepository
from game.repository.config import SessionRepositoryConfig, SessionRepositoryType
from game.repository.redis_session_repository import RedisSessionRepository


class SessionRepositoryProvider:
    """
    The one place a session repository is constructed.
    """

    @staticmethod
    def get_session_repository(config: SessionRepositoryConfig) -> BaseSessionRepository:
        """
        The store the configuration selects, holding its own settings.

        Raises ValueError when the selected store has no builder, or when its
        settings section is missing.
        """
        builder = SessionRepositoryProvider.BUILDERS_BY_TYPE.get(config.repository)
        if builder is None:
            raise ValueError(
                f"no session repository is registered for {config.repository.value!r}; "
                f"known repositories are "
                f"{', '.join(sorted(SessionRepositoryProvider.BUILDERS_BY_TYPE))}"
            )
        return builder(config)

    @staticmethod
    def _build_redis_session_repository(config: SessionRepositoryConfig) -> BaseSessionRepository:
        if config.redis_config is None:
            raise ValueError(
                f"session repository is {SessionRepositoryType.REDIS.value!r} but redis_config "
                f"is missing; add a redis_config section to the configuration file"
            )
        return RedisSessionRepository(config=config.redis_config)

    # Keys are data — a repository type names its builder. This is a lookup, not
    # a record, and it follows the builders it names.
    BUILDERS_BY_TYPE: ClassVar[
        dict[SessionRepositoryType, Callable[[SessionRepositoryConfig], BaseSessionRepository]]
    ] = {
        SessionRepositoryType.REDIS: _build_redis_session_repository,
    }
