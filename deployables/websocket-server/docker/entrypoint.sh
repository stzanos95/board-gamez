#!/bin/sh
# The one place that knows how to run anything in this image.
#
# The app is run from source rather than from the installed wheel, so that
# bind-mounting the source for development takes effect without a rebuild.
set -eu

: "${APP_DIR:=/app/deployables/websocket-server}"
# The app is brought up from a YAML file and reads no environment of its own,
# so the path is handed to it as an argument. Passing --config yourself wins.
: "${WEBSOCKET_SERVER_CONFIG:=$APP_DIR/config/websocket_server.yaml}"

COMMAND="${1:-serve}"
if [ "$#" -gt 0 ]; then
    shift
fi

case "$COMMAND" in
    serve)
        exec python "$APP_DIR/src_python/main.py" --config "$WEBSOCKET_SERVER_CONFIG" "$@"
        ;;
    test)
        cd "$APP_DIR" && exec python -m pytest "$@"
        ;;
    lint)
        # Both halves of what the pre-commit hook runs, so a green container is
        # a green commit: the rules, then the formatting.
        cd "$APP_DIR" && python -m ruff check "$@" && exec python -m ruff format --check "$@"
        ;;
    typecheck)
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
