# Sourced by the other idl scripts. Locates the repository and the compose file,
# so every script works from any directory.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IDL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$IDL_DIR/.." && pwd)"
INFRA_DIR="$REPO_ROOT/infra"

IDL_COMPOSE="$INFRA_DIR/compose/docker-compose.idl.yml"

# Generated files are written through a bind mount. Without these the container
# writes them as root, and the host can then neither edit nor delete its own
# generated code.
IDL_USER_ID="$(id -u)"
IDL_GROUP_ID="$(id -g)"
export IDL_USER_ID IDL_GROUP_ID

require_docker() {
    if ! command -v docker >/dev/null 2>&1; then
        echo "docker is not installed, and the IDL toolchain lives in a container." >&2
        echo "  ./setup.sh --with-docker" >&2
        exit 1
    fi
}

# `run --rm`, not `up`: this is a task that finishes, not a service.
#
# --build on every run because the image is a set of pinned versions, and a
# stale one generates code from a toolchain the Dockerfile no longer describes.
# Buildkit answers in about a second when nothing has changed, and bumping a pin
# then needs no one to remember to rebuild.
idl_compose_run() {
    docker compose -f "$IDL_COMPOSE" run --rm --build idl "$@"
}
