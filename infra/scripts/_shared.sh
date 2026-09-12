# Sourced by the other infra scripts. Locates the repository and the compose
# files, so every script works from any directory.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$INFRA_DIR/.." && pwd)"
COMPOSE_DIR="$INFRA_DIR/compose"

BASE_COMPOSE="$COMPOSE_DIR/docker-compose.yml"
DEV_COMPOSE="$COMPOSE_DIR/docker-compose.dev.yml"
TEST_COMPOSE="$COMPOSE_DIR/docker-compose.test.yml"

require_docker() {
    if ! command -v docker >/dev/null 2>&1; then
        echo "docker is not installed. Either:" >&2
        echo "  ./setup.sh --with-docker" >&2
        echo "or serve without a container:" >&2
        echo "  ./deployables/fastapi-gateway/scripts/local-serve.sh" >&2
        exit 1
    fi
}

compose() {
    docker compose "$@"
}
