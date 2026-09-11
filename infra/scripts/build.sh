#!/usr/bin/env bash
# Build every deployable's image, the CLI included.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
require_docker
compose --profile cli -f "$BASE_COMPOSE" build "$@"
