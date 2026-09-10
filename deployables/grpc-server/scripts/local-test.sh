#!/usr/bin/env bash
# Run the server's suite on this machine, without a container.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
cd "$REPO_ROOT/deployables/grpc-server"
require_uv
exec uv run --quiet python -m unittest discover -s tests -t . "$@"
