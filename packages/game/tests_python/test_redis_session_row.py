import unittest

from google.protobuf.timestamp_pb2 import Timestamp
from idl.core.obj.object_metadata_pb2 import ObjectMetadata
from idl.game.obj.session_pb2 import SessionObj

from game.repository.redis_session_row import (
    NO_DEADLINE_SCORE,
    DeadlineIndexEntry,
    RedisSessionRow,
)

KEY_PREFIX = "gamez"
SESSION_ID = "t-1"
VERSION = 4
ACTS_BY_MILLISECONDS = 1_767_225_600_123


def acts_by() -> Timestamp:
    instant = Timestamp()
    instant.FromMilliseconds(ACTS_BY_MILLISECONDS)
    return instant


class DeadlineIndexTest(unittest.TestCase):
    def test_the_index_is_one_key_per_deployment(self) -> None:
        self.assertEqual(RedisSessionRow.deadline_index_key(KEY_PREFIX), "gamez:deadline")

    def test_a_session_with_a_deadline_is_scored_by_it_in_milliseconds(self) -> None:
        session = SessionObj(metadata=ObjectMetadata(id=SESSION_ID), acts_by=acts_by())
        self.assertEqual(RedisSessionRow.encode_deadline_score(session), str(ACTS_BY_MILLISECONDS))

    def test_a_session_without_a_deadline_has_no_score(self) -> None:
        session = SessionObj(metadata=ObjectMetadata(id=SESSION_ID))
        self.assertEqual(RedisSessionRow.encode_deadline_score(session), NO_DEADLINE_SCORE)

    def test_a_range_item_becomes_an_entry(self) -> None:
        entry = RedisSessionRow.range_item_to_index_entry((b"t-1", float(ACTS_BY_MILLISECONDS)))
        self.assertEqual(
            entry, DeadlineIndexEntry(session_id=SESSION_ID, score=ACTS_BY_MILLISECONDS)
        )

    def test_a_range_item_without_a_score_is_refused(self) -> None:
        with self.assertRaises(TypeError):
            RedisSessionRow.range_item_to_index_entry(b"t-1")

    def test_an_entry_and_the_sessions_version_make_a_deadline(self) -> None:
        entry = DeadlineIndexEntry(session_id=SESSION_ID, score=ACTS_BY_MILLISECONDS)
        deadline = RedisSessionRow.index_entry_to_deadline(entry, b"4")
        self.assertEqual(deadline.metadata.id, SESSION_ID)
        self.assertEqual(deadline.metadata.version, VERSION)
        self.assertEqual(deadline.acts_by, acts_by())
