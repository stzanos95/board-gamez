#!/usr/bin/env bash
# Build the chess-cli image.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
require_docker
compose -f "$BASE_COMPOSE" build "$@"
