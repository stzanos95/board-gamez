#!/usr/bin/env bash
# Type-check this deployable and the ux package it draws from.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
require_docker
ensure_dependencies
node_run npm run typecheck -- "$@"
