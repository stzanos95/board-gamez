#!/usr/bin/env bash
# Bring up the whole stack detached, building any image that is missing: the
# store, the gRPC server on 50051, the gateway on 8080, and the interface on
# 8081. Each browser tab is a different player.
#
# ./infra/scripts/down.sh stops everything.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
require_docker
compose -f "$BASE_COMPOSE" up --build --detach "$@"
