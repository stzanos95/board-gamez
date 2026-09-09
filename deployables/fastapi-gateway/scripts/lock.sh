#!/usr/bin/env bash
# Write uv.lock, using uv inside a container so the host never installs it.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
require_docker
exec docker run --rm \
    --volume "$REPO_ROOT:/repo" \
    --workdir /repo/deployables/fastapi-gateway \
    --user "$(id -u):$(id -g)" \
    ghcr.io/astral-sh/uv:python3.13-bookworm-slim \
    uv lock "$@"
