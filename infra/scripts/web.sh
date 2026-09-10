#!/usr/bin/env bash
# Serve the whole stack in containers: the interface, the gateway, the server
# and the store.
#
# Open http://127.0.0.1:8081 — each browser tab is a different player.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
require_docker
compose -f "$BASE_COMPOSE" up "$@" gamez-ux
