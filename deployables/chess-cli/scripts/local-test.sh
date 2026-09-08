#!/usr/bin/env bash
# Run both suites on this machine, without a container.
#
# The engine has no dependencies, so it runs under any Python 3.13 or newer. The
# app parses its settings with mashumaro, so it runs under uv. Set
# CHESS_SLOW_TESTS=1 to include the deep perft counts.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"

ENGINE_DIR="$REPO_ROOT/packages/chess"
APP_DIR="$REPO_ROOT/deployables/chess-cli"

echo "--- engine ---"
cd "$ENGINE_DIR"
PYTHONPATH="$ENGINE_DIR/src_python" python3 -m unittest discover -s tests_python -t . "$@"

echo "--- chess-cli ---"
cd "$APP_DIR"
require_uv
uv run --quiet python -m unittest discover -s tests -t . "$@"
