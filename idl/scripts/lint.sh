#!/usr/bin/env bash
# Lint the schema. Naming, versioned packages, enum zero values, RPC shapes.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
require_docker
idl_compose_run lint "$@"
