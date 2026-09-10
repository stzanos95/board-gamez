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
COPY deployables/fastapi-gateway /app/deployables/fastapi-gateway

WORKDIR /app/deployables/fastapi-gateway
# Includes the dev group, so the same image can run the tests, the linter and the
# type checker.
RUN uv sync --no-install-project


FROM python:3.13-slim-bookworm AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app/deployables/fastapi-gateway/src_python" \
    APP_DIR="/app/deployables/fastapi-gateway" \
    FASTAPI_GATEWAY_CONFIG="/app/deployables/fastapi-gateway/config/fastapi_gateway.container.yaml"

RUN useradd --create-home --uid 1000 gateway

COPY --from=builder --chown=gateway:gateway /opt/venv /opt/venv
COPY --chown=gateway:gateway idl/contracts/gen/python /app/idl/contracts/gen/python
COPY --chown=gateway:gateway idl/contracts/gen/fastapi /app/idl/contracts/gen/fastapi
COPY --chown=gateway:gateway packages/core /app/packages/core
COPY --chown=gateway:gateway packages/lobby /app/packages/lobby
COPY --chown=gateway:gateway deployables/fastapi-gateway /app/deployables/fastapi-gateway
COPY deployables/fastapi-gateway/docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

USER gateway
WORKDIR /app

# Documentation only, and it must match the port in the config file the image
# ships with. The listener speaks plain HTTP; TLS is terminated ahead of it.
EXPOSE 8080

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["serve"]
