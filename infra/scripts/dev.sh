#!/usr/bin/env bash
# Run a service with the host source bind-mounted, so edits apply without a
# rebuild. Defaults to the game; name another service to run that instead.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
require_docker
SERVICE="${1:-chess-cli}"
if [ "$#" -gt 0 ]; then
    shift
fi
compose -f "$BASE_COMPOSE" -f "$DEV_COMPOSE" run --rm "$SERVICE" "$@"
