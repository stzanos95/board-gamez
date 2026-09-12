#!/usr/bin/env bash
# Run every suite in a container.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
require_docker
compose -f "$BASE_COMPOSE" -f "$TEST_COMPOSE" run --rm fastapi-gateway "$@"
