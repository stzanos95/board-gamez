#!/usr/bin/env bash
# Build every deployable's image.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
require_docker
compose -f "$BASE_COMPOSE" build "$@"
