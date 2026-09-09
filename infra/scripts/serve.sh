#!/usr/bin/env bash
# Serve the gateway in a container, publishing the port its config names.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
require_docker
compose -f "$BASE_COMPOSE" up "$@" fastapi-gateway
