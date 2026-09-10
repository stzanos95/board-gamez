# syntax=docker/dockerfile:1

# The build context is the repository ROOT, not this directory: this deployable
# reaches its domain package, the shared utilities and the generated contracts
# through relative paths, so all four trees must be present. Those dependencies
# are installed editable, which records the path rather than copying the code,
# so the runtime stage needs the same trees at the same places.
# infra/compose/docker-compose.yml sets that context.

FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

# The environment is deliberately outside the app tree. Bind-mounting the source
# for development would otherwise shadow a virtualenv living inside it.
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app
COPY idl/contracts/gen/python /app/idl/contracts/gen/python
COPY idl/contracts/gen/fastapi /app/idl/contracts/gen/fastapi
COPY packages/core /app/packages/core
COPY packages/lobby /app/packages/lobby
COPY deployables/grpc-server /app/deployables/grpc-server

WORKDIR /app/deployables/grpc-server
# Includes the dev group, so the same image can run the tests, the linter and the
# type checker.
RUN uv sync --no-install-project


FROM python:3.13-slim-bookworm AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app/deployables/grpc-server/src_python" \
    APP_DIR="/app/deployables/grpc-server" \
    GRPC_SERVER_CONFIG="/app/deployables/grpc-server/config/grpc_server.container.yaml"

RUN useradd --create-home --uid 1000 server

COPY --from=builder --chown=server:server /opt/venv /opt/venv
COPY --chown=server:server idl/contracts/gen/python /app/idl/contracts/gen/python
COPY --chown=server:server idl/contracts/gen/fastapi /app/idl/contracts/gen/fastapi
COPY --chown=server:server packages/core /app/packages/core
COPY --chown=server:server packages/lobby /app/packages/lobby
COPY --chown=server:server deployables/grpc-server /app/deployables/grpc-server
COPY deployables/grpc-server/docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

USER server
WORKDIR /app

# Documentation only, and it must match the port in the config file the image
# ships with. The listener speaks plain HTTP/2; transport security is terminated
# ahead of it.
EXPOSE 50051

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["serve"]
