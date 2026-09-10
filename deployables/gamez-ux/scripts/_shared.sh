# Sourced by the other scripts. Locates the repository and runs the node
# toolchain, so nothing has to be installed on this machine.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UX_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$UX_DIR/../.." && pwd)"

# Pinned, so the same toolchain builds the same bundle on any machine. Moving it
# means moving the builder stage in docker/Dockerfile with it.
NODE_IMAGE="node:22-alpine"

require_docker() {
    if ! command -v docker >/dev/null 2>&1; then
        echo "docker is not installed, and the node toolchain lives in a container." >&2
        echo "  ./setup.sh --with-docker" >&2
        exit 1
    fi
}

# The whole repository is mounted rather than this deployable alone: the two
# packages it draws from are TypeScript source at paths outside it.
#
# The container runs as the host user. Without that, node_modules and dist are
# written as root and the host can neither edit nor delete what it produced.
#
# Host networking, so the dev server is reachable at the port it names and the
# gateway is reachable at 127.0.0.1 the same way it is from a shell here.
node_run() {
    node_run_in /repo/deployables/gamez-ux "$@"
}

# The TypeScript side is one npm workspace, rooted at the repository. Installing
# there is what puts a single copy of React, MUI and the contracts where every
# source tree can resolve them.
node_run_root() {
    node_run_in /repo "$@"
}

node_run_in() {
    local workdir="$1"
    shift
    docker run --rm -i \
        --network host \
        -u "$(id -u):$(id -g)" \
        -e HOME=/tmp \
        -e npm_config_cache=/tmp/.npm \
        -v "$REPO_ROOT:/repo" \
        -w "$workdir" \
        "$NODE_IMAGE" "$@"
}

ensure_dependencies() {
    if [ ! -d "$REPO_ROOT/node_modules" ]; then
        echo "installing dependencies (first run)" >&2
        node_run_root npm install --no-audit --no-fund
    fi
}
