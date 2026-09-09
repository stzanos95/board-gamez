"""
Entry point for the HTTP gateway.

Reads the configuration file named on the command line, builds the gateway from
it, and serves until the process is stopped. The path is required: what to run
with is chosen outside this process, never guessed inside it.
"""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from fastapi_gateway.gateway_api import GatewayAPI
from fastapi_gateway.gateway_api_config import GatewayAPIConfig

EXIT_SUCCESS = 0

PROGRAM_NAME = "fastapi-gateway"
CONFIG_OPTION = "--config"
CONFIG_ENCODING = "utf-8"


def main(argv: Sequence[str] | None = None) -> int:
    """
    The console-script entry point, which must be a module-level function.

    A configuration file that is missing, malformed, or not settings raises here
    and stops the process before anything listens.
    """
    parser = argparse.ArgumentParser(
        prog=PROGRAM_NAME, description="Serve the board-gamez HTTP gateway."
    )
    parser.add_argument(
        CONFIG_OPTION,
        type=Path,
        required=True,
        help="settings file to bring the app up from",
    )
    arguments = parser.parse_args(argv)
    with arguments.config.open(encoding=CONFIG_ENCODING) as config_file:
        config = GatewayAPIConfig.from_yaml(config_file.read())
    GatewayAPI(config=config).start()
    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
