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
# Same shape again: hand-written packaging at the root, generated code in src/.
: "${FASTAPI_PACKAGE_DIR:=$GEN_DIR/fastapi}"
: "${FASTAPI_OUT_DIR:=$FASTAPI_PACKAGE_DIR/src}"
# Its own root package: the protobuf target already publishes a top-level `idl`,
# and two distributions cannot both own that name.
: "${FASTAPI_ROOT_PACKAGE:=idl_fastapi}"
: "${FASTAPI_PACKAGE_NAME:=idl-fastapi}"
: "${CODEGEN_VENV:=/opt/codegen}"

: "${TYPESCRIPT_TARGET:=ts}"
: "${OPENAPI_TITLE:=board-gamez chess API}"
: "${OPENAPI_DOCUMENT_VERSION:=1.0.0}"
# JSON names and string enums, because the wire format these describe is proto3
# canonical JSON. An integer enum in a JSON body is unreadable in a log.
: "${OPENAPI_NAMING:=json}"
: "${OPENAPI_ENUM_TYPE:=string}"
# Schema names carry their proto package. Two domains may both declare a Table,
# and short names would leave one of them silently renamed.
: "${OPENAPI_FQ_SCHEMA_NAMING:=true}"

# The packaging that ships beside the generated code is rendered, not committed
# by hand, so nothing under contracts/gen survives a regeneration unchanged by
# accident. envsubst substitutes ${NAME} and nothing else.
: "${TEMPLATE_DIR:=$IDL_DIR/scripts/templates}"
: "${CONTRACTS_VERSION:=0.1.0}"
: "${PYTHON_PACKAGE_NAME:=board-gamez-idl}"
: "${FASTAPI_MIN_VERSION:=0.141.1}"
: "${PYDANTIC_MIN_VERSION:=2.13}"
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

# Only files that declare a service produce gRPC stubs. Handing protoc the rest
# would write an empty _pb2_grpc.py beside every message file.
our_service_proto_files() {
    grep -rl '^service ' "$PROTO_DIR" --include='*.proto' | sort
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
    # The generated servicers import grpc, so the distribution that ships them
    # asks for the runtime that matches the tools which wrote them.
    GRPCIO_VERSION="${GRPCIO_TOOLS_VERSION:-1.68.1}"
    export PYTHON_PACKAGE_NAME CONTRACTS_VERSION ROOT_PACKAGE
    export PYTHON_PROTOBUF_VERSION PYTHON_PROTOBUF_MAJOR_BOUND GRPCIO_VERSION
    render_template "$TEMPLATE_DIR/pyproject.toml.template" \
        "$PYTHON_PACKAGE_DIR/pyproject.toml" \
        '${PYTHON_PACKAGE_NAME} ${CONTRACTS_VERSION} ${ROOT_PACKAGE} ${PYTHON_PROTOBUF_VERSION} ${PYTHON_PROTOBUF_MAJOR_BOUND} ${GRPCIO_VERSION}'
}

write_typescript_packaging() {
    # The runtime a consumer installs and the plugin that wrote the code are one
    # release, so the image's own pin is the version the package asks for.
    export TYPESCRIPT_PACKAGE_NAME CONTRACTS_VERSION ROOT_PACKAGE PROTOC_GEN_ES_VERSION
    render_template "$TEMPLATE_DIR/package.json.template" \
        "$TYPESCRIPT_PACKAGE_DIR/package.json" \
        '${TYPESCRIPT_PACKAGE_NAME} ${CONTRACTS_VERSION} ${ROOT_PACKAGE} ${PROTOC_GEN_ES_VERSION}'
}

write_fastapi_packaging() {
    export FASTAPI_PACKAGE_NAME CONTRACTS_VERSION FASTAPI_ROOT_PACKAGE
    export FASTAPI_MIN_VERSION PYDANTIC_MIN_VERSION
    render_template "$TEMPLATE_DIR/fastapi-pyproject.toml.template" \
        "$FASTAPI_PACKAGE_DIR/pyproject.toml" \
        '${FASTAPI_PACKAGE_NAME} ${CONTRACTS_VERSION} ${FASTAPI_ROOT_PACKAGE} ${FASTAPI_MIN_VERSION} ${PYDANTIC_MIN_VERSION}'
}

# The servicer and the client stub for every service, written beside the message
# modules they import.
#
# grpc_tools carries its own protoc because the gRPC Python plugin lives inside
# protoc rather than beside it, so this is the one target the pinned protoc
# cannot drive.
generate_grpc() {
    services="$(our_service_proto_files)"
    if [ -z "$services" ]; then
        echo "  grpc        -> no service declared"
        return 0
    fi
    # shellcheck disable=SC2046,SC2086
    "$CODEGEN_VENV/bin/python" -m grpc_tools.protoc \
        --proto_path="$PROTO_DIR" \
        --proto_path="$THIRD_PARTY_DIR" \
        --plugin=protoc-gen-mypy_grpc="$CODEGEN_VENV/bin/protoc-gen-mypy_grpc" \
        --grpc_python_out="$PYTHON_OUT_DIR" \
        --mypy_grpc_out="$PYTHON_OUT_DIR" \
        $services
    echo "  grpc        -> $(echo "$services" | wc -l) service files"
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

    generate_grpc

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
        --openapi_opt="fq_schema_naming=$OPENAPI_FQ_SCHEMA_NAMING" \
        $(our_proto_files)
    echo "  openapi     -> ${OPENAPI_OUT_DIR#"$IDL_DIR"/}"
}

generate_fastapi() {
    # Reads the OpenAPI document rather than the .proto files, so it runs after
    # the openapi target and fails if that one has not written yet.
    document="$OPENAPI_OUT_DIR/openapi.yaml"
    if [ ! -f "$document" ]; then
        echo "no OpenAPI document at $document; run the openapi target first" >&2
        exit 1
    fi
    reset_output_directory "$FASTAPI_OUT_DIR"
    package_root="$FASTAPI_OUT_DIR/$FASTAPI_ROOT_PACKAGE"

    # The models first: a schema named idl.lobby.dto.Table becomes Table in the
    # module idl/lobby/dto.py, which is what the routers import it from.
    #
    # Literal enum fields rather than Enum classes, because a proto enum is
    # inlined into the field that carries it: the generator would name its class
    # after that field and number the duplicates, so adding a message could
    # renumber a class every consumer imports by name.
    # Two warnings are expected on every run and say nothing a reader can act on:
    # protoc-gen-openapi writes `format: uint32` and `format: enum`, which are not
    # JSON Schema formats, so the generator falls back to the base type. They are
    # dropped by name below, and anything else it says still reaches the terminal.
    codegen_warnings="$(mktemp)"
    if ! "$CODEGEN_VENV/bin/datamodel-codegen" \
        --input "$document" \
        --input-file-type openapi \
        --output "$package_root" \
        --output-model-type pydantic_v2.BaseModel \
        --target-python-version 3.13 \
        --use-standard-collections \
        --use-union-operator \
        --use-schema-description \
        --snake-case-field \
        --allow-population-by-field-name \
        --enum-field-as-literal all \
        --use-default-kwarg \
        --disable-timestamp \
        --formatters builtin 2>"$codegen_warnings"; then
        cat "$codegen_warnings" >&2
        rm -f "$codegen_warnings"
        exit 1
    fi
    grep -v -e "UserWarning: format of" -e "return _get_type" "$codegen_warnings" >&2 || true
    rm -f "$codegen_warnings"
    echo "  fastapi     -> ${FASTAPI_OUT_DIR#"$IDL_DIR"/}"

    "$CODEGEN_VENV/bin/python" /usr/local/bin/render_routers.py \
        --document "$document" \
        --output "$package_root/services" \
        --root-package "$FASTAPI_ROOT_PACKAGE"

    # PEP 561, as for the protobuf target: without it a consumer's type checker
    # reads the whole distribution as untyped.
    touch "$package_root/py.typed"
    write_fastapi_packaging
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
        generate_fastapi
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
    fastapi)
        generate_fastapi
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
        reset_output_directory "$FASTAPI_OUT_DIR"
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
