#!/usr/bin/env bash
# Play a game in a container. `run`, not `up`, so the prompt gets a terminal.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
require_docker
compose -f "$BASE_COMPOSE" run --rm chess-cli "$@"
