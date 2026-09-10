#!/usr/bin/env bash
# Run npm against the workspace, inside the pinned node image.
#
#   scripts/npm.sh install
#   scripts/npm.sh run typecheck
#
# install runs at the repository root, because that is where the workspace is.
# Everything else runs in this deployable.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
require_docker

case "${1:-}" in
    install | ci | update)
        node_run_root npm "$@"
        ;;
    *)
        node_run npm "$@"
        ;;
esac
