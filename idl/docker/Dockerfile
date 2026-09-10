# syntax=docker/dockerfile:1

# The IDL toolchain, and nothing else.
#
# The build context is this directory, not the repository root: the image holds
# tools, never schemas. proto/ and gen/ arrive as a bind mount at run time, so
# editing a .proto and regenerating never rebuilds this image.
#
# Every version is pinned in the block below, and that block is the only place
# to bump one. An unpinned toolchain generates different code on different days,
# which is the one thing generated code must never do.

ARG BUF_VERSION=1.47.2
ARG PROTOC_VERSION=28.3
ARG PROTOC_GEN_ES_VERSION=2.2.2
ARG PROTOC_GEN_OPENAPI_VERSION=v0.7.0
ARG DATAMODEL_CODEGEN_VERSION=0.78.0
ARG GRPCIO_TOOLS_VERSION=1.68.1
ARG MYPY_PROTOBUF_VERSION=3.6.0
ARG GO_VERSION=1.23
ARG NODE_VERSION=22


# protoc-gen-openapi is a Go program with no published binary, so it is built.
FROM golang:${GO_VERSION}-bookworm AS openapi-plugin

ARG PROTOC_GEN_OPENAPI_VERSION
ENV CGO_ENABLED=0 \
    GOBIN=/out
RUN go install "github.com/google/gnostic/cmd/protoc-gen-openapi@${PROTOC_GEN_OPENAPI_VERSION}"


# Node is the base rather than a stage, because protoc-gen-es is a node program
# and needs an interpreter when protoc runs it, not only when it is installed.
FROM node:${NODE_VERSION}-bookworm-slim AS toolchain

ARG BUF_VERSION
ARG PROTOC_VERSION
ARG PROTOC_GEN_ES_VERSION
ARG TARGETARCH

RUN apt-get update \
    && apt-get install --no-install-recommends --yes \
        ca-certificates curl gettext-base git unzip python3 python3-venv \
    && rm -rf /var/lib/apt/lists/*

# The FastAPI and gRPC targets are written by Python tools, which Debian will not
# let pip install system-wide. They get their own environment, off PATH, so that
# `python3` in this image stays the interpreter and nothing else.
#
# grpcio-tools carries its own protoc, and it is the only way to reach the gRPC
# Python plugin: unlike the others that plugin ships inside protoc rather than
# beside it. mypy-protobuf writes the .pyi for what it produces, without which
# every servicer would be untyped to a consumer running mypy strict.
ARG DATAMODEL_CODEGEN_VERSION
ARG GRPCIO_TOOLS_VERSION
ARG MYPY_PROTOBUF_VERSION
ENV CODEGEN_VENV=/opt/codegen
RUN python3 -m venv "$CODEGEN_VENV" \
    && "$CODEGEN_VENV/bin/pip" install --no-cache-dir --quiet \
        "datamodel-code-generator==${DATAMODEL_CODEGEN_VERSION}" \
        "grpcio-tools==${GRPCIO_TOOLS_VERSION}" \
        "mypy-protobuf==${MYPY_PROTOBUF_VERSION}"

# protoc and buf spell the same architectures differently, so both are mapped
# from the one name buildkit supplies.
RUN set -eux; \
    case "${TARGETARCH}" in \
        amd64) protoc_arch=x86_64; buf_arch=x86_64 ;; \
        arm64) protoc_arch=aarch_64; buf_arch=aarch64 ;; \
        *) echo "unsupported architecture ${TARGETARCH}" >&2; exit 1 ;; \
    esac; \
    curl --fail --silent --show-error --location \
        --output /tmp/protoc.zip \
        "https://github.com/protocolbuffers/protobuf/releases/download/v${PROTOC_VERSION}/protoc-${PROTOC_VERSION}-linux-${protoc_arch}.zip"; \
    unzip -q /tmp/protoc.zip -d /usr/local 'bin/protoc' 'include/*'; \
    rm /tmp/protoc.zip; \
    chmod +x /usr/local/bin/protoc; \
    curl --fail --silent --show-error --location \
        --output /usr/local/bin/buf \
        "https://github.com/bufbuild/buf/releases/download/v${BUF_VERSION}/buf-Linux-${buf_arch}"; \
    chmod +x /usr/local/bin/buf

# The runtime is installed beside the plugin, not left to npm. protoc-gen-es
# imports @bufbuild/protobuf when it starts, and a global install does not pull
# a peer dependency in — the plugin then dies on its first invocation with a
# module-not-found, which protoc reports only as a plugin that returned nothing.
# The two are released in lockstep, so they share a version.
RUN npm install --global --no-fund --no-audit \
    "@bufbuild/protoc-gen-es@${PROTOC_GEN_ES_VERSION}" \
    "@bufbuild/protobuf@${PROTOC_GEN_ES_VERSION}"

COPY --from=openapi-plugin /out/protoc-gen-openapi /usr/local/bin/protoc-gen-openapi

# The container runs as the host user's uid so that generated files are owned by
# whoever ran the script. That uid has no home directory, and git and buf both
# want somewhere to write.
#
# The repository root is mounted, not idl/ alone, because `buf breaking` reads
# the baseline schema out of .git.
ENV HOME=/tmp \
    REPO_ROOT=/repo \
    IDL_DIR=/repo/idl \
    PROTOC_GEN_ES_VERSION=${PROTOC_GEN_ES_VERSION} \
    GRPCIO_TOOLS_VERSION=${GRPCIO_TOOLS_VERSION}

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
COPY render_routers.py /usr/local/bin/render_routers.py
RUN chmod +x /usr/local/bin/entrypoint.sh

# Proving the toolchain works here means a broken pin fails the build, rather
# than failing the first generate with an empty output directory.
RUN set -eux; \
    protoc --version; \
    buf --version; \
    test -x /usr/local/bin/protoc-gen-openapi; \
    "$CODEGEN_VENV/bin/datamodel-codegen" --version; \
    "$CODEGEN_VENV/bin/python" -m grpc_tools.protoc --version; \
    test -x "$CODEGEN_VENV/bin/protoc-gen-mypy_grpc"; \
    npm ls --global --depth=0

WORKDIR /repo/idl
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["generate"]
