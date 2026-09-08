#!/usr/bin/env bash
# Run the linter and the type checker in a container.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
require_docker
compose -f "$BASE_COMPOSE" -f "$TEST_COMPOSE" run --rm chess-lint
compose -f "$BASE_COMPOSE" -f "$TEST_COMPOSE" run --rm chess-typecheck
