#!/usr/bin/env bash
# Regenerate idl/contracts/gen from idl/contracts/proto.
#
#   generate.sh              every target
#   generate.sh typescript   one of them, when a single generator is misbehaving
#
# Naming one target is also how you see its errors on their own: a failing
# generator stops the whole run, so the targets after it never write anything.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
require_docker

TARGET="${1:-all}"

case "$TARGET" in
    all)
        idl_compose_run generate
        ;;
    python | typescript | openapi | fastapi)
        idl_compose_run "$TARGET"
        ;;
    *)
        echo "unknown target ${TARGET}" >&2
        echo "usage: generate.sh [all|python|typescript|openapi|fastapi]" >&2
        exit 2
        ;;
esac
