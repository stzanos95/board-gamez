#!/usr/bin/env bash
# Bring up every backend service, building any image that is missing.
#
# The gateway on 8080 and the gRPC server on 50051. Ctrl-C stops both.
# Pass --detach to leave them running.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
require_docker
compose -f "$BASE_COMPOSE" up --build "$@" grpc-server fastapi-gateway
