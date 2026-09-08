#!/usr/bin/env bash
# Refuse a schema change that would break a client speaking the version on main.
#
# Renaming a field, renumbering one, changing its type or moving a message to
# another file are all caught here. Adding a field or a message is not: that is
# the whole point of a versioned wire format.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
require_docker
idl_compose_run breaking "$@"
