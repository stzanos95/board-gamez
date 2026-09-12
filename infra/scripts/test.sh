#!/usr/bin/env bash
# Run every suite in a container: each package's, then each deployable's.
# No dependency is started; no suite reaches a store or a port.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
require_docker
compose -f "$BASE_COMPOSE" -f "$TEST_COMPOSE" run --rm --no-deps package-tests "$@"
compose -f "$BASE_COMPOSE" -f "$TEST_COMPOSE" run --rm --no-deps fastapi-gateway "$@"
compose -f "$BASE_COMPOSE" -f "$TEST_COMPOSE" run --rm --no-deps grpc-server "$@"
compose -f "$BASE_COMPOSE" -f "$TEST_COMPOSE" run --rm --no-deps websocket-server "$@"
