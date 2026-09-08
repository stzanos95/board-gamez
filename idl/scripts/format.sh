#!/usr/bin/env bash
# Format the .proto files in place. --check reports instead of rewriting.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
require_docker
if [ "${1:-}" = "--check" ]; then
    shift
    idl_compose_run format-check "$@"
else
    idl_compose_run format "$@"
fi
