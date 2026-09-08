#!/usr/bin/env bash
# Play with the host source bind-mounted, so edits apply without a rebuild.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
require_docker
compose -f "$BASE_COMPOSE" -f "$DEV_COMPOSE" run --rm chess-cli "$@"
