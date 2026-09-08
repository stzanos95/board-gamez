#!/usr/bin/env bash
# Play on this machine, without a container.
#
# Pass --config to use settings other than deployables/chess-cli/config/chess_cli.yaml.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
cd "$REPO_ROOT/deployables/chess-cli"
require_uv
exec uv run --quiet python src_python/main.py "$@"
