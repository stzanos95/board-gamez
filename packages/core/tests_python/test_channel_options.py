import unittest

from core.grpc.channel_options import (
    MAX_RECEIVE_MESSAGE_LENGTH,
    MAX_SEND_MESSAGE_LENGTH,
    ChannelOptions,
)

RECEIVE_LIMIT = 1024
SEND_LIMIT = 2048


class ChannelOptionsTest(unittest.TestCase):
    def test_the_limits_reach_grpc_under_the_names_it_knows(self) -> None:
        options = dict(
            ChannelOptions(
                max_receive_message_bytes=RECEIVE_LIMIT, max_send_message_bytes=SEND_LIMIT
            ).to_options()
        )
        self.assertEqual(options[MAX_RECEIVE_MESSAGE_LENGTH], RECEIVE_LIMIT)
        self.assertEqual(options[MAX_SEND_MESSAGE_LENGTH], SEND_LIMIT)

    def test_every_configured_limit_is_carried(self) -> None:
        options = ChannelOptions(
            max_receive_message_bytes=RECEIVE_LIMIT, max_send_message_bytes=SEND_LIMIT
        ).to_options()
        self.assertEqual(len(options), 2)
