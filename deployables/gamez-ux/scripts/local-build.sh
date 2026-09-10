#!/usr/bin/env bash
# Type-check and build the bundle into dist/.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
require_docker
ensure_dependencies
node_run npm run build -- "$@"
