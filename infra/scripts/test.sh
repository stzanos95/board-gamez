#!/usr/bin/env bash
# Run both test suites in a container. CHESS_SLOW_TESTS=1 adds the deep perft counts.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
require_docker
compose -f "$BASE_COMPOSE" -f "$TEST_COMPOSE" run --rm chess-cli "$@"
