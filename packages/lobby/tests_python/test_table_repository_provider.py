import unittest

from lobby.repository.config import (
    RedisTableRepositoryConfig,
    TableRepositoryConfig,
    TableRepositoryType,
)
from lobby.repository.provider import TableRepositoryProvider
from lobby.repository.redis_table_repository import RedisTableRepository

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_DATABASE = 0
KEY_PREFIX = "board-gamez-test"


class TableRepositoryProviderTest(unittest.TestCase):
    """
    The store the configuration selects, and what a configuration that selects
    one without configuring it does.
    """

    def test_the_configured_store_is_the_one_that_is_built(self) -> None:
        config = TableRepositoryConfig(
            repository=TableRepositoryType.REDIS,
            redis_config=RedisTableRepositoryConfig(
                host=REDIS_HOST,
                port=REDIS_PORT,
                database=REDIS_DATABASE,
                key_prefix=KEY_PREFIX,
            ),
        )

        self.assertIsInstance(
            TableRepositoryProvider.get_table_repository(config), RedisTableRepository
        )

    def test_a_store_selected_without_its_settings_stops_bringup(self) -> None:
        config = TableRepositoryConfig(repository=TableRepositoryType.REDIS)

        with self.assertRaises(ValueError) as raised:
            TableRepositoryProvider.get_table_repository(config)

        self.assertIn("redis_config", str(raised.exception))
