# Sourced by the other scripts. Locates the repository and the compose files so
# every script can be run from anywhere.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
INFRA_DIR="$REPO_ROOT/infra"

require_uv() {
    if ! command -v uv >/dev/null 2>&1; then
        echo "uv is not installed. Run ./setup.sh from the repository root." >&2
        exit 1
    fi
}

require_docker() {
    if ! command -v docker >/dev/null 2>&1; then
        echo "docker is not installed. To run the game without it:" >&2
        echo "  deployables/chess-cli/scripts/local-play.sh" >&2
        echo "  deployables/chess-cli/scripts/local-test.sh" >&2
        exit 1
    fi
}
