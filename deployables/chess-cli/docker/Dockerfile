# syntax=docker/dockerfile:1

# The build context is the repository ROOT, not this directory: the deployable
# depends on the engine through a relative path, so both trees must be present.
# infra/docker-compose.yml sets that context.

FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

# The environment is deliberately outside the app tree. Bind-mounting the source
# for development would otherwise shadow a virtualenv living inside it.
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app
COPY idl/contracts/gen/python /app/idl/contracts/gen/python
COPY packages/chess /app/packages/chess
COPY deployables/chess-cli /app/deployables/chess-cli

WORKDIR /app/deployables/chess-cli
# Includes the dev group, so the same image can run the tests, the linter and the
# type checker.
RUN uv sync --no-install-project


FROM python:3.13-slim-bookworm AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app/packages/chess/src_python:/app/deployables/chess-cli/src_python" \
    ENGINE_DIR="/app/packages/chess" \
    APP_DIR="/app/deployables/chess-cli" \
    CHESS_CLI_CONFIG="/app/deployables/chess-cli/config/chess_cli.yaml"

RUN useradd --create-home --uid 1000 player

COPY --from=builder --chown=player:player /opt/venv /opt/venv
COPY --chown=player:player idl/contracts/gen/python /app/idl/contracts/gen/python
COPY --chown=player:player packages/chess /app/packages/chess
COPY --chown=player:player deployables/chess-cli /app/deployables/chess-cli
COPY deployables/chess-cli/docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

USER player
WORKDIR /app

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["play"]
