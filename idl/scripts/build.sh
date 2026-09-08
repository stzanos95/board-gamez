#!/usr/bin/env bash
# Build the IDL toolchain image. Rarely needed: every version is pinned in the
# Dockerfile, so the image only changes when one of those pins does.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
require_docker
docker compose -f "$IDL_COMPOSE" build "$@"
