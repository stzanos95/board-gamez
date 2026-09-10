#!/usr/bin/env bash
# Serve the interface on this machine, rebuilding as files change.
#
# Calls to the gateway are forwarded by the dev server, so the browser makes no
# cross-origin request. Start the gateway first:
#   ../fastapi-gateway/scripts/local-serve.sh
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
require_docker
ensure_dependencies
node_run npm run dev -- "$@"
