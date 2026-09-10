#!/usr/bin/env bash
# Stop every backend service and remove its containers.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
require_docker
compose -f "$BASE_COMPOSE" down "$@"
