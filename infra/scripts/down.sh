#!/usr/bin/env bash
# Stop every service of the stack, remove its containers and its network, and
# remove any container left over from a service no longer in the compose file.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
require_docker
compose --profile cli -f "$BASE_COMPOSE" down --remove-orphans "$@"
