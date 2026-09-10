#!/bin/sh
# The one place that knows how to run anything in this image.
set -eu

COMMAND="${1:-serve}"
if [ "$#" -gt 0 ]; then
    shift
fi

case "$COMMAND" in
    serve)
        exec nginx -g "daemon off;" "$@"
        ;;
    shell)
        exec /bin/sh "$@"
        ;;
    *)
        exec "$COMMAND" "$@"
        ;;
esac
