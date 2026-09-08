#!/bin/sh
# The one place that knows how to run anything in this image.
#
# The app is run from source rather than from the installed wheel, so that
# bind-mounting the source for development takes effect without a rebuild.
set -eu

: "${ENGINE_DIR:=/app/packages/chess}"
: "${APP_DIR:=/app/deployables/chess-cli}"
# The app is brought up from a YAML file and reads no environment of its own,
# so the path is handed to it as an argument. Passing --config yourself wins.
: "${CHESS_CLI_CONFIG:=$APP_DIR/config/chess_cli.yaml}"

COMMAND="${1:-play}"
if [ "$#" -gt 0 ]; then
    shift
fi

case "$COMMAND" in
    play)
        exec python "$APP_DIR/src_python/main.py" --config "$CHESS_CLI_CONFIG" "$@"
        ;;
    test)
        cd "$ENGINE_DIR" && python -m pytest "$@"
        cd "$APP_DIR" && exec python -m pytest "$@"
        ;;
    lint)
        # Both halves of what the pre-commit hook runs, so a green container is
        # a green commit: the rules, then the formatting.
        cd "$ENGINE_DIR" && python -m ruff check "$@" && python -m ruff format --check "$@"
        cd "$APP_DIR" && python -m ruff check "$@" && exec python -m ruff format --check "$@"
        ;;
    typecheck)
        cd "$ENGINE_DIR" && python -m mypy "$@"
        cd "$APP_DIR" && exec python -m mypy "$@"
        ;;
    shell)
        exec /bin/sh "$@"
        ;;
    *)
        # Anything else is run verbatim, which keeps one-off commands possible
        # without teaching this script about each of them.
        exec "$COMMAND" "$@"
        ;;
esac
