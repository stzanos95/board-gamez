#!/usr/bin/env bash
# Serve on this machine, without a container.
#
# The app never guesses where its settings are, so the path is named here.
# Passing --config yourself wins, since argparse takes the last one given.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
GATEWAY_DIR="$REPO_ROOT/deployables/fastapi-gateway"
cd "$GATEWAY_DIR"
require_uv
exec uv run --quiet python src_python/main.py \
    --config "$GATEWAY_DIR/config/fastapi_gateway.yaml" "$@"
