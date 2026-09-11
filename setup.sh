#!/usr/bin/env bash
#
# setup.sh — prepare this machine to build, test and play everything in this repo.
#
# Idempotent by construction. Every step is an "ensure": it checks the state it
# wants before touching anything, reports what it found, and acts only on the
# difference. Running this twice does exactly what running it once did, and
# running it after a failure part-way through resumes rather than duplicating.
# Nothing here removes or overwrites anything you already have.
#
#   ./setup.sh                  install uv, build the Python environments, verify
#   ./setup.sh --with-docker    also install Docker Engine if it is missing (sudo)
#   ./setup.sh --skip-image     do not build the container image
#   ./setup.sh --skip-tests     do not run the test suites at the end
#   ./setup.sh --help

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IDL_PYTHON_DIR="$REPO_ROOT/idl/contracts/gen/python"
IDL_FASTAPI_DIR="$REPO_ROOT/idl/contracts/gen/fastapi"
CORE_DIR="$REPO_ROOT/packages/core"
ENGINE_DIR="$REPO_ROOT/packages/chess"
LOBBY_DIR="$REPO_ROOT/packages/lobby"
GAME_DIR="$REPO_ROOT/packages/game"
PRODUCT_CHESS_DIR="$REPO_ROOT/packages/product-chess"
APP_DIR="$REPO_ROOT/deployables/chess-cli"
SERVER_DIR="$REPO_ROOT/deployables/grpc-server"
GATEWAY_DIR="$REPO_ROOT/deployables/fastapi-gateway"
INFRA_DIR="$REPO_ROOT/infra"
DEV_VENV_DIR="$REPO_ROOT/.dev-venv"
DEV_VENV_PYTHON="$DEV_VENV_DIR/bin/python"

UV_INSTALL_URL="https://astral.sh/uv/install.sh"
USER_BIN_DIR="$HOME/.local/bin"
PROFILE_FILE="$HOME/.bashrc"
PROFILE_MARKER="# >>> board-gamez setup >>>"
MINIMUM_PYTHON_MINOR=13
DOCKER_PACKAGES=(docker.io docker-compose-v2 docker-buildx)
# Kept in step with default_install_hook_types in .pre-commit-config.yaml.
HOOK_TYPES=(pre-commit pre-push)

WITH_DOCKER=0
SKIP_IMAGE=0
SKIP_TESTS=0

# Whether anything actually changed, so the closing summary can say so honestly.
CHANGES_MADE=0
DOCKER_USABLE=0
NEEDS_RELOGIN=0

if [ -t 1 ]; then
    BOLD=$'\033[1m'; DIM=$'\033[2m'; GREEN=$'\033[32m'; YELLOW=$'\033[33m'
    RED=$'\033[31m'; RESET=$'\033[0m'
else
    BOLD=""; DIM=""; GREEN=""; YELLOW=""; RED=""; RESET=""
fi

step()    { printf '\n%s==> %s%s\n' "$BOLD" "$1" "$RESET"; }
ok()      { printf '    %s✓%s %s\n' "$GREEN" "$RESET" "$1"; }
already() { printf '    %s·%s %s %s(already in place)%s\n' "$DIM" "$RESET" "$1" "$DIM" "$RESET"; }
changed() { CHANGES_MADE=1; printf '    %s+%s %s\n' "$GREEN" "$RESET" "$1"; }
warn()    { printf '    %s!%s %s\n' "$YELLOW" "$RESET" "$1"; }
fail()    { printf '    %sx%s %s\n' "$RED" "$RESET" "$1" >&2; }
note()    { printf '      %s%s%s\n' "$DIM" "$1" "$RESET"; }

usage() {
    sed -n '2,20p' "${BASH_SOURCE[0]}" | sed 's/^#\{1,2\} \{0,1\}//'
    exit 0
}

parse_arguments() {
    while [ "$#" -gt 0 ]; do
        case "$1" in
            --with-docker) WITH_DOCKER=1 ;;
            --skip-image)  SKIP_IMAGE=1 ;;
            --skip-tests)  SKIP_TESTS=1 ;;
            -h|--help)     usage ;;
            *)
                fail "unknown option $1"
                echo "Run ./setup.sh --help for the options." >&2
                exit 2
                ;;
        esac
        shift
    done
}

# --- environment -----------------------------------------------------------

report_environment() {
    step "Looking at this machine"
    local description="unknown"
    if [ -r /etc/os-release ]; then
        # shellcheck disable=SC1091
        description="$(. /etc/os-release && printf '%s' "$PRETTY_NAME")"
    fi
    ok "$description ($(uname -m))"
    if grep -qi microsoft /proc/version 2>/dev/null; then
        ok "running under WSL"
    fi
    if command -v python3 >/dev/null 2>&1; then
        ok "system python: $(python3 --version 2>&1)"
    else
        warn "no system python3 — uv will supply its own interpreter"
    fi
}

system_python_is_new_enough() {
    command -v python3 >/dev/null 2>&1 || return 1
    python3 - "$MINIMUM_PYTHON_MINOR" <<'PY' >/dev/null 2>&1
import sys
sys.exit(0 if sys.version_info[:2] >= (3, int(sys.argv[1])) else 1)
PY
}

# --- uv --------------------------------------------------------------------

ensure_path_entry() {
    # Put ~/.local/bin on PATH for this run, and once — never twice — in the profile.
    case ":$PATH:" in
        *":$USER_BIN_DIR:"*) : ;;
        *) PATH="$USER_BIN_DIR:$PATH"; export PATH ;;
    esac

    if [ ! -f "$PROFILE_FILE" ] || ! grep -qF "$PROFILE_MARKER" "$PROFILE_FILE"; then
        {
            printf '\n%s\n' "$PROFILE_MARKER"
            printf 'export PATH="$HOME/.local/bin:$PATH"\n'
            printf '%s\n' "# <<< board-gamez setup <<<"
        } >>"$PROFILE_FILE"
        changed "added $USER_BIN_DIR to PATH in $(basename "$PROFILE_FILE")"
        note "open a new shell, or run: export PATH=\"\$HOME/.local/bin:\$PATH\""
    else
        already "$USER_BIN_DIR is on PATH in $(basename "$PROFILE_FILE")"
    fi
}

ensure_uv() {
    step "uv"
    ensure_path_entry
    if command -v uv >/dev/null 2>&1; then
        already "uv $(uv --version 2>&1 | awk '{print $2}') at $(command -v uv)"
        return 0
    fi

    local downloader
    if command -v curl >/dev/null 2>&1; then
        downloader="curl -LsSf $UV_INSTALL_URL"
    elif command -v wget >/dev/null 2>&1; then
        downloader="wget -qO- $UV_INSTALL_URL"
    else
        fail "neither curl nor wget is available, so uv cannot be fetched"
        note "install one of them, or install uv yourself: https://docs.astral.sh/uv/"
        return 1
    fi

    if ! $downloader | sh >/dev/null 2>&1; then
        fail "the uv installer did not complete — is there a network connection?"
        return 1
    fi
    hash -r
    if ! command -v uv >/dev/null 2>&1; then
        fail "uv installed but is not on PATH; expected it at $USER_BIN_DIR"
        return 1
    fi
    changed "installed uv $(uv --version 2>&1 | awk '{print $2}')"
}

# --- python environments ---------------------------------------------------

# A virtualenv is not relocatable. Its console scripts — ruff, mypy, pytest, the
# `chess` entry point — carry the absolute path of the interpreter that created
# them in their shebang, so renaming or moving the checkout breaks every one of
# them. uv cannot see this: .venv/bin/python is a symlink that still resolves, so
# the environment looks healthy and a plain `uv sync` leaves the stale scripts
# alone. Detecting it is therefore this script's job, not uv's.
project_venv_is_stale() {
    local venv="$1/.venv"
    [ -d "$venv" ] || return 1

    local script interpreter
    for script in "$venv"/bin/*; do
        [ -f "$script" ] || continue
        interpreter="$(sed -n '1s/^#!\([^[:space:]]*\).*/\1/p' "$script" 2>/dev/null)"
        case "$interpreter" in
            */python*)
                # The first console script settles it: they are all written together.
                [ "${interpreter#"$venv"/}" = "$interpreter" ] && return 0
                return 1
                ;;
        esac
    done
    return 1
}

ensure_project_environment() {
    local project_dir="$1" label="$2"
    local had_lock=0 had_venv=0 was_stale=0
    [ -f "$project_dir/uv.lock" ] && had_lock=1
    [ -d "$project_dir/.venv" ] && had_venv=1

    # Reinstalling is what rewrites the shebangs; syncing alone will not.
    local sync_arguments=(--quiet)
    if project_venv_is_stale "$project_dir"; then
        was_stale=1
        sync_arguments+=(--reinstall)
    fi

    if ! (cd "$project_dir" && uv sync "${sync_arguments[@]}"); then
        fail "uv sync failed for $label"
        return 1
    fi

    if [ "$had_lock" -eq 0 ]; then
        changed "$label: wrote uv.lock"
    else
        already "$label: uv.lock"
    fi
    if [ "$had_venv" -eq 0 ]; then
        changed "$label: created .venv"
    elif [ "$was_stale" -eq 1 ]; then
        changed "$label: rebuilt .venv — it was built somewhere else"
    else
        already "$label: .venv"
    fi
}

ensure_project_environments() {
    step "Python environments"
    if ! command -v uv >/dev/null 2>&1; then
        warn "skipping — uv is not available"
        return 0
    fi
    ensure_project_environment "$CORE_DIR" "packages/core"
    ensure_project_environment "$ENGINE_DIR" "packages/chess"
    ensure_project_environment "$LOBBY_DIR" "packages/lobby"
    ensure_project_environment "$GAME_DIR" "packages/game"
    ensure_project_environment "$PRODUCT_CHESS_DIR" "packages/product-chess"
    ensure_project_environment "$APP_DIR" "deployables/chess-cli"
    ensure_project_environment "$SERVER_DIR" "deployables/grpc-server"
    ensure_project_environment "$GATEWAY_DIR" "deployables/fastapi-gateway"
}

# --- one environment for the editor -----------------------------------------

# Each project has an environment of its own, and that is what the hooks and the
# scripts use. An editor holds one interpreter at a time, so following an import
# from one project into another needs an environment holding every project.
# This one does, installed editable, so a definition resolves to the file in the
# checkout rather than to a copy.
#
# Everything is installed in one command on purpose: the projects depend on each
# other by name, and none of those names is on an index, so they resolve only
# because the same command provides them.
DEV_VENV_PROJECTS=(
    "$IDL_PYTHON_DIR"
    "$IDL_FASTAPI_DIR"
    "$CORE_DIR"
    "$ENGINE_DIR"
    "$LOBBY_DIR"
    "$GAME_DIR"
    "$PRODUCT_CHESS_DIR"
    "$APP_DIR"
    "$SERVER_DIR"
    "$GATEWAY_DIR"
)
# ruff is pinned to the rev in .pre-commit-config.yaml, so the editor and the
# hook format identically.
DEV_VENV_TOOLS=(
    "pytest>=9.1.1"
    "mypy>=2.3.1"
    "ruff==0.16.6"
    "types-protobuf>=5.28"
    "types-grpcio>=1.83"
    "types-grpcio-reflection>=1.0"
)

ensure_dev_venv() {
    step "Editor environment"
    if ! command -v uv >/dev/null 2>&1; then
        warn "skipping — uv is not available"
        return 0
    fi

    local had_venv=0
    [ -x "$DEV_VENV_PYTHON" ] && had_venv=1
    if [ "$had_venv" -eq 0 ] && ! uv venv --quiet --python "3.$MINIMUM_PYTHON_MINOR" "$DEV_VENV_DIR"; then
        fail "could not create $DEV_VENV_DIR"
        return 1
    fi

    local install_arguments=()
    local project
    for project in "${DEV_VENV_PROJECTS[@]}"; do
        install_arguments+=(--editable "$project")
    done
    # Idempotent: uv changes only what differs from what is asked for.
    if ! uv pip install --quiet --python "$DEV_VENV_PYTHON" \
        "${install_arguments[@]}" "${DEV_VENV_TOOLS[@]}"; then
        fail "could not install the projects into $DEV_VENV_DIR"
        return 1
    fi

    if [ "$had_venv" -eq 0 ]; then
        changed "created .dev-venv with every project installed editable"
    else
        already ".dev-venv"
    fi
    note "point the editor at $DEV_VENV_PYTHON"
}

# --- git hooks -------------------------------------------------------------

ensure_git_hooks() {
    step "Git hooks"
    if [ ! -d "$REPO_ROOT/.git" ]; then
        warn "skipped — this is not a git checkout"
        return 0
    fi
    if ! command -v uv >/dev/null 2>&1; then
        warn "skipped — uv is not available"
        return 0
    fi

    # A uv *tool*, not `uvx`: the hook script git writes points at this
    # executable, so it has to outlive the command that installed it. It lands in
    # ~/.local/bin, which ensure_path_entry has already put on PATH.
    if uv tool list 2>/dev/null | grep -q "^pre-commit "; then
        already "pre-commit $(pre-commit --version 2>/dev/null | awk '{print $2}')"
    elif uv tool install --quiet pre-commit >/dev/null 2>&1; then
        hash -r
        changed "installed pre-commit $(pre-commit --version 2>&1 | awk '{print $2}')"
    else
        warn "could not install pre-commit — commits will not be checked"
        return 0
    fi

    # Both hook types, because .pre-commit-config.yaml asks for both: ruff on
    # every commit, mypy on every push.
    local hook_type
    local missing=0
    for hook_type in "${HOOK_TYPES[@]}"; do
        if ! grep -qs pre-commit "$REPO_ROOT/.git/hooks/$hook_type"; then
            missing=1
        fi
    done
    if [ "$missing" -eq 0 ]; then
        already "git hooks: ${HOOK_TYPES[*]}"
        return 0
    fi

    # --install-hooks builds the hook environments now, so the first commit after
    # setup is not the one that pays for downloading them.
    if (cd "$REPO_ROOT" && pre-commit install --install-hooks >/dev/null 2>&1); then
        changed "wired git hooks: ${HOOK_TYPES[*]}"
    else
        warn "could not wire the git hooks"
    fi
}

# --- docker ----------------------------------------------------------------

docker_daemon_responds() {
    docker info >/dev/null 2>&1
}

ensure_docker_group_membership() {
    if id -nG "$USER" 2>/dev/null | tr ' ' '\n' | grep -qx docker; then
        already "$USER is in the docker group"
        return 0
    fi
    if ! getent group docker >/dev/null 2>&1; then
        warn "there is no docker group to join yet"
        return 0
    fi
    if sudo usermod -aG docker "$USER"; then
        changed "added $USER to the docker group"
        NEEDS_RELOGIN=1
    else
        warn "could not add $USER to the docker group; docker will need sudo"
    fi
}

ensure_docker_daemon_running() {
    if docker_daemon_responds; then
        ok "the docker daemon is responding"
        DOCKER_USABLE=1
        return 0
    fi
    if [ "$(ps -p 1 -o comm= 2>/dev/null)" = "systemd" ]; then
        if systemctl is-active --quiet docker; then
            warn "docker is running but not responding to this user"
        else
            if sudo systemctl enable --now docker >/dev/null 2>&1; then
                changed "started the docker service and enabled it at boot"
            else
                warn "could not start the docker service"
            fi
        fi
    else
        if sudo service docker start >/dev/null 2>&1; then
            changed "started the docker service"
        else
            warn "could not start the docker service"
        fi
    fi

    if docker_daemon_responds; then
        DOCKER_USABLE=1
        ok "the docker daemon is responding"
    elif [ "$NEEDS_RELOGIN" -eq 1 ]; then
        warn "docker is installed but this shell predates your docker group membership"
        note "log out and back in, or run: newgrp docker"
    else
        warn "docker is installed but the daemon is not reachable"
    fi
}

install_docker_packages() {
    local missing=()
    local package
    for package in "${DOCKER_PACKAGES[@]}"; do
        if ! dpkg-query -W -f='${Status}' "$package" 2>/dev/null | grep -q "ok installed"; then
            missing+=("$package")
        fi
    done
    if [ "${#missing[@]}" -eq 0 ]; then
        already "docker packages: ${DOCKER_PACKAGES[*]}"
        return 0
    fi

    if ! command -v apt-get >/dev/null 2>&1; then
        fail "this is not an apt-based system; install docker yourself"
        return 1
    fi
    warn "installing: ${missing[*]} (this needs sudo)"
    sudo apt-get update -qq
    sudo apt-get install -y -qq "${missing[@]}"
    changed "installed ${missing[*]}"
}

ensure_docker() {
    step "Docker"
    if command -v docker >/dev/null 2>&1; then
        already "docker $(docker --version 2>&1 | awk '{print $3}' | tr -d ,)"
        ensure_docker_group_membership
        ensure_docker_daemon_running
        return 0
    fi

    if [ "$WITH_DOCKER" -eq 0 ]; then
        warn "docker is not installed, and this script will not install it unless asked"
        note "to install it:  ./setup.sh --with-docker"
        note "everything except the container workflow works without it."
        return 0
    fi

    install_docker_packages || return 0
    hash -r
    ensure_docker_group_membership
    ensure_docker_daemon_running
}

ensure_docker_image() {
    step "Container image"
    if [ "$SKIP_IMAGE" -eq 1 ]; then
        warn "skipped by --skip-image"
        return 0
    fi
    if [ "$DOCKER_USABLE" -eq 0 ]; then
        warn "skipped — no usable docker daemon"
        note "once docker works:  ./infra/scripts/build.sh"
        return 0
    fi
    # Rebuilding is cheap and idempotent: unchanged layers come from the cache.
    if (cd "$INFRA_DIR" && docker compose -f compose/docker-compose.yml build); then
        ok "the deployable images are up to date"
    else
        fail "the image build failed"
        return 1
    fi
}

ensure_infra_env_file() {
    step "Local settings"
    if [ -f "$INFRA_DIR/.env" ]; then
        already "infra/.env"
        return 0
    fi
    cp "$INFRA_DIR/.env.example" "$INFRA_DIR/.env"
    changed "created infra/.env from .env.example"
}

# --- verification ----------------------------------------------------------

run_test_suites() {
    step "Verifying"
    if [ "$SKIP_TESTS" -eq 1 ]; then
        warn "skipped by --skip-tests"
        return 0
    fi
    if ! system_python_is_new_enough && ! command -v uv >/dev/null 2>&1; then
        warn "skipped — no python 3.$MINIMUM_PYTHON_MINOR or newer, and no uv"
        return 0
    fi
    if "$APP_DIR/scripts/local-test.sh" >/tmp/board-gamez-setup-tests.log 2>&1 &&
        "$GATEWAY_DIR/scripts/local-test.sh" >>/tmp/board-gamez-setup-tests.log 2>&1 &&
        (cd "$LOBBY_DIR" && uv run --quiet python -m unittest discover -s tests_python -t .) \
            >>/tmp/board-gamez-setup-tests.log 2>&1; then
        ok "$(grep -c '^OK' /tmp/board-gamez-setup-tests.log) suites passed"
        grep -E '^Ran ' /tmp/board-gamez-setup-tests.log | while read -r line; do note "$line"; done
    else
        fail "the test suites did not pass"
        tail -30 /tmp/board-gamez-setup-tests.log >&2
        return 1
    fi
}

summarise() {
    step "Ready"
    if [ "$CHANGES_MADE" -eq 0 ]; then
        ok "nothing needed changing — this machine was already set up"
    fi
    echo
    echo "  Play now, with no container:"
    echo "      ./deployables/chess-cli/scripts/local-play.sh"
    echo
    echo "  Serve the gateway, with no container:"
    echo "      ./deployables/fastapi-gateway/scripts/local-serve.sh"
    echo
    echo "  Run the tests:"
    echo "      ./deployables/chess-cli/scripts/local-test.sh"
    echo "      ./deployables/fastapi-gateway/scripts/local-test.sh"
    echo
    echo "  Settings live in a file, not the environment:"
    echo "      deployables/chess-cli/config/chess_cli.yaml"
    echo "      deployables/fastapi-gateway/config/fastapi_gateway.yaml"
    echo
    echo "  Commits are checked for you — ruff on commit, mypy on push:"
    echo "      pre-commit run --all-files"
    echo
    echo "  Every project in one environment, for the editor:"
    echo "      $DEV_VENV_PYTHON"
    echo
    if [ "$DOCKER_USABLE" -eq 1 ]; then
        echo "  Play in the container, or serve the gateway from one:"
        echo "      ./infra/scripts/play.sh"
        echo "      ./infra/scripts/serve.sh"
        echo
        echo "  Check everything the way CI would:"
        echo "      ./infra/scripts/test.sh"
        echo "      ./infra/scripts/lint.sh"
    else
        echo "  Container workflow is not available yet."
        echo "      ./setup.sh --with-docker"
    fi
    if [ "$NEEDS_RELOGIN" -eq 1 ]; then
        echo
        warn "log out and back in before using docker without sudo"
    fi
    echo
}

main() {
    parse_arguments "$@"
    printf '%sboard-gamez setup%s\n' "$BOLD" "$RESET"
    report_environment
    ensure_uv || true
    ensure_project_environments || true
    ensure_dev_venv || true
    ensure_git_hooks || true
    ensure_docker
    ensure_infra_env_file
    ensure_docker_image || true
    run_test_suites
    summarise
}

main "$@"
