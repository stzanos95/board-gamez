#!/bin/sh
# The one place that knows how to run anything in this image.
#
# Generation is driven by protoc rather than by `buf generate`, because all three
# targets are plain protoc plugins and the flags below say exactly what each one
# receives. buf is still here, and owns what it is best at: linting, formatting
# and breaking-change detection.
#
# Every path and plugin option is a variable with a default, so a one-off run can
# override one without editing this file.
set -eu

: "${REPO_ROOT:=/repo}"
: "${IDL_DIR:=$REPO_ROOT/idl}"
# The schema and everything it compiles to. Tooling — this image, the
# scripts, buf.yaml, the vendored includes — sits outside it.
: "${CONTRACTS_DIR:=$IDL_DIR/contracts}"
: "${PROTO_DIR:=$CONTRACTS_DIR/proto}"
: "${GEN_DIR:=$CONTRACTS_DIR/gen}"
: "${THIRD_PARTY_DIR:=$IDL_DIR/third_party}"

# The Python target is an installable distribution, not a loose tree: its
# pyproject.toml sits at the root and is written by hand, so generated code goes
# one level down into src/ where emptying it cannot take the packaging with it.
: "${PYTHON_PACKAGE_DIR:=$GEN_DIR/python}"
: "${PYTHON_OUT_DIR:=$PYTHON_PACKAGE_DIR/src}"
# Same shape as the Python target: hand-written packaging at the root, generated
# code one level down in src/ where emptying it cannot take the packaging with it.
: "${TYPESCRIPT_PACKAGE_DIR:=$GEN_DIR/typescript}"
: "${TYPESCRIPT_OUT_DIR:=$TYPESCRIPT_PACKAGE_DIR/src}"
: "${OPENAPI_OUT_DIR:=$GEN_DIR/openapi}"

: "${TYPESCRIPT_TARGET:=ts}"
: "${OPENAPI_TITLE:=board-gamez chess API}"
: "${OPENAPI_DOCUMENT_VERSION:=1.0.0}"
# JSON names and string enums, because the wire format these describe is proto3
# canonical JSON. An integer enum in a JSON body is unreadable in a log.
: "${OPENAPI_NAMING:=json}"
: "${OPENAPI_ENUM_TYPE:=string}"

# The packaging that ships beside the generated code is rendered, not committed
# by hand, so nothing under contracts/gen survives a regeneration unchanged by
# accident. envsubst substitutes ${NAME} and nothing else.
: "${TEMPLATE_DIR:=$IDL_DIR/scripts/templates}"
: "${CONTRACTS_VERSION:=0.1.0}"
: "${PYTHON_PACKAGE_NAME:=board-gamez-idl}"
: "${TYPESCRIPT_PACKAGE_NAME:=@board-gamez/idl}"
# The single top-level package the generated tree publishes, which is the first
# path segment of every .proto under contracts/proto.
: "${ROOT_PACKAGE:=idl}"

: "${BREAKING_BASELINE_BRANCH:=main}"

# A directory that git will refuse to read when the container's uid does not own
# the checkout, which it never does.
git_is_safe_here() {
    git config --global --add safe.directory "$REPO_ROOT" >/dev/null 2>&1 || true
}

# The files we generate from, newline separated and in a stable order so that
# regenerating an unchanged tree produces an unchanged diff.
#
# Everything under contracts/proto is ours. third_party is an include path
# only: it is compiled so that imports resolve, and never generated from.
our_proto_files() {
    find "$PROTO_DIR" -name '*.proto' -type f | sort
}

# protoc fails obscurely when handed no files at all, so say what is wrong.
require_proto_files() {
    if [ -z "$(our_proto_files)" ]; then
        echo "no .proto files under $PROTO_DIR" >&2
        exit 1
    fi
}

vendored_proto_files() {
    find "$THIRD_PARTY_DIR" -name '*.proto' -type f | sort
}

# Emptied rather than overwritten: a message that is deleted from a .proto must
# not leave its generated class behind, still importable and now a lie.
reset_output_directory() {
    rm -rf "${1:?}"
    mkdir -p "$1"
}

render_template() {
    template="$1"
    destination="$2"
    # Named explicitly, so a $ in the template that is not one of these is left
    # alone rather than silently blanked.
    variables="$3"
    if [ ! -f "$template" ]; then
        echo "missing template $template" >&2
        exit 1
    fi
    envsubst "$variables" <"$template" >"$destination"
    echo "  packaging   -> ${destination#"$IDL_DIR"/}"
}

write_python_packaging() {
    generated="$(find "$PYTHON_OUT_DIR" -name '*_pb2.py' -type f | sort | head -1)"
    if [ -z "$generated" ]; then
        echo "nothing was generated under $PYTHON_OUT_DIR to package" >&2
        exit 1
    fi
    # protoc stamps the runtime it targets into every file it writes, and the
    # generated modules refuse to import under anything older. Reading it back is
    # what keeps the dependency floor from drifting away from the toolchain pin.
    PYTHON_PROTOBUF_VERSION="$(sed -n 's/^# Protobuf Python Version: *//p' "$generated" | head -1)"
    if [ -z "$PYTHON_PROTOBUF_VERSION" ]; then
        echo "could not read the protobuf runtime version out of $generated" >&2
        exit 1
    fi
    protobuf_major="${PYTHON_PROTOBUF_VERSION%%.*}"
    PYTHON_PROTOBUF_MAJOR_BOUND="$((protobuf_major + 1))"
    export PYTHON_PACKAGE_NAME CONTRACTS_VERSION ROOT_PACKAGE
    export PYTHON_PROTOBUF_VERSION PYTHON_PROTOBUF_MAJOR_BOUND
    render_template "$TEMPLATE_DIR/pyproject.toml.template" \
        "$PYTHON_PACKAGE_DIR/pyproject.toml" \
        '${PYTHON_PACKAGE_NAME} ${CONTRACTS_VERSION} ${ROOT_PACKAGE} ${PYTHON_PROTOBUF_VERSION} ${PYTHON_PROTOBUF_MAJOR_BOUND}'
}

write_typescript_packaging() {
    # The runtime a consumer installs and the plugin that wrote the code are one
    # release, so the image's own pin is the version the package asks for.
    export TYPESCRIPT_PACKAGE_NAME CONTRACTS_VERSION ROOT_PACKAGE PROTOC_GEN_ES_VERSION
    render_template "$TEMPLATE_DIR/package.json.template" \
        "$TYPESCRIPT_PACKAGE_DIR/package.json" \
        '${TYPESCRIPT_PACKAGE_NAME} ${CONTRACTS_VERSION} ${ROOT_PACKAGE} ${PROTOC_GEN_ES_VERSION}'
}

generate_python() {
    reset_output_directory "$PYTHON_OUT_DIR"
    # shellcheck disable=SC2046
    protoc \
        --proto_path="$PROTO_DIR" \
        --proto_path="$THIRD_PARTY_DIR" \
        --python_out="$PYTHON_OUT_DIR" \
        --pyi_out="$PYTHON_OUT_DIR" \
        $(our_proto_files)

    # protoc writes the package directories but no __init__.py, so nothing it
    # produced is importable until these exist. They stay empty, which is what
    # the house style asks of every __init__.py anyway.
    find "$PYTHON_OUT_DIR" -mindepth 1 -type d -exec touch {}/__init__.py \;

    # PEP 561: without this marker a type checker ignores the .pyi files next
    # door and reports the whole distribution as untyped. One per top-level
    # package, which is where the marker has to sit to be found.
    find "$PYTHON_OUT_DIR" -mindepth 1 -maxdepth 1 -type d -exec touch {}/py.typed \;

    # google/api is deliberately NOT generated here. It would put a top-level
    # `google` package on sys.path that shadows the real one, and
    # `import google.protobuf` would stop working. Python consumers get those
    # two modules from the googleapis-common-protos wheel instead.
    echo "  python      -> ${PYTHON_OUT_DIR#"$IDL_DIR"/}"
    write_python_packaging
}

generate_typescript() {
    reset_output_directory "$TYPESCRIPT_OUT_DIR"
    # The vendored files are generated here, unlike for Python: TypeScript has no
    # ambient `google` namespace to collide with, and a generated service file
    # imports its annotations, so they have to exist by the time one does.
    # Generating them now keeps contracts/gen/typescript from changing shape.
    # shellcheck disable=SC2046
    protoc \
        --proto_path="$PROTO_DIR" \
        --proto_path="$THIRD_PARTY_DIR" \
        --es_out="$TYPESCRIPT_OUT_DIR" \
        --es_opt="target=$TYPESCRIPT_TARGET" \
        $(our_proto_files) $(vendored_proto_files)
    echo "  typescript  -> ${TYPESCRIPT_OUT_DIR#"$IDL_DIR"/}"
    write_typescript_packaging
}

generate_openapi() {
    reset_output_directory "$OPENAPI_OUT_DIR"
    # protoc-gen-openapi walks services, not messages: HTTP annotations produce
    # the paths, and the messages those methods touch follow as component
    # schemas. Until contracts/proto/idl/chess/service holds a service, this writes
    # a valid document with nothing in it. That is expected, not a failure.
    # shellcheck disable=SC2046
    protoc \
        --proto_path="$PROTO_DIR" \
        --proto_path="$THIRD_PARTY_DIR" \
        --openapi_out="$OPENAPI_OUT_DIR" \
        --openapi_opt="title=$OPENAPI_TITLE" \
        --openapi_opt="version=$OPENAPI_DOCUMENT_VERSION" \
        --openapi_opt="naming=$OPENAPI_NAMING" \
        --openapi_opt="enum_type=$OPENAPI_ENUM_TYPE" \
        $(our_proto_files)
    echo "  openapi     -> ${OPENAPI_OUT_DIR#"$IDL_DIR"/}"
}

COMMAND="${1:-generate}"
if [ "$#" -gt 0 ]; then
    shift
fi

cd "$IDL_DIR"

case "$COMMAND" in
    generate)
        require_proto_files
        echo "generating from $(our_proto_files | wc -l) proto files"
        generate_python
        generate_typescript
        generate_openapi
        ;;
    python)
        require_proto_files
        generate_python
        ;;
    typescript)
        require_proto_files
        generate_typescript
        ;;
    openapi)
        require_proto_files
        generate_openapi
        ;;
    lint)
        exec buf lint "$@"
        ;;
    format)
        exec buf format --write "$@"
        ;;
    format-check)
        exec buf format --diff --exit-code "$@"
        ;;
    breaking)
        # The baseline is the schema as it stands on the main branch, so the
        # check answers "does this change break a client that is already live".
        git_is_safe_here
        exec buf breaking \
            --against "$REPO_ROOT/.git#branch=$BREAKING_BASELINE_BRANCH,subdir=idl" "$@"
        ;;
    clean)
        reset_output_directory "$PYTHON_OUT_DIR"
        reset_output_directory "$TYPESCRIPT_OUT_DIR"
        reset_output_directory "$OPENAPI_OUT_DIR"
        echo "emptied $GEN_DIR"
        ;;
    shell)
        exec /bin/sh "$@"
        ;;
    *)
        # Anything else runs verbatim, which keeps a one-off protoc or buf
        # invocation possible without teaching this script about it.
        exec "$COMMAND" "$@"
        ;;
esac
