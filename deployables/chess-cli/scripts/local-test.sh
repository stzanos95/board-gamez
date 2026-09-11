#!/usr/bin/env bash
# Run both suites on this machine, without a container.
#
# The engine reads and answers the schema's records, so both projects run under
# uv, each from its own environment. Set CHESS_SLOW_TESTS=1 to include the deep
# perft counts.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"

ENGINE_DIR="$REPO_ROOT/packages/chess"
APP_DIR="$REPO_ROOT/deployables/chess-cli"

require_uv

echo "--- engine ---"
cd "$ENGINE_DIR"
uv run --quiet python -m unittest discover -s tests_python -t . "$@"

echo "--- chess-cli ---"
cd "$APP_DIR"
uv run --quiet python -m unittest discover -s tests -t . "$@"
