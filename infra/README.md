# infra

Everything that lifts a deployable into a container.

```
compose/     the compose files
scripts/     thin wrappers over them, runnable from anywhere
.env.example test switches only — app settings live in the deployable's config/
```

## Scripts

```bash
scripts/build.sh    build every deployable's image
scripts/play.sh     play a game
scripts/serve.sh    serve the gateway on the port its config names
scripts/up.sh       serve the whole stack detached, interface included, on 8081
scripts/down.sh     stop and remove every container of the stack
scripts/dev.sh      run a service with the host source bind-mounted, no rebuild
scripts/test.sh     every test suite
scripts/lint.sh     ruff and mypy
```

`serve.sh` uses `docker compose up`, so the published port reaches the host. It
must match the port in `deployables/fastapi-gateway/config/fastapi_gateway.yaml`
— compose publishes the port, and the app binds it.

`play.sh` uses `docker compose run`, not `up` — an interactive prompt needs stdin
attached, which `up` does not do.

`compose/docker-compose.idl.yml` is the one compose file here with no script
beside it. The IDL toolchain is driven from where the schema lives:

```bash
../idl/scripts/generate.sh    # and lint.sh, format.sh, breaking.sh, check.sh
```

It is also the one whose build context is a directory of tools rather than the
repository root. That image holds no schema — `idl/contracts` arrives through a
bind mount, so editing a `.proto` never rebuilds it.

`dev.sh` bind-mounts the source trees read-only. Safe because the virtualenv
lives at `/opt/venv`, outside them. Editing a deployable's config file takes
effect on the next run. It runs `chess-cli` unless another service is named:
`scripts/dev.sh fastapi-gateway`.

`CHESS_SLOW_TESTS=1` adds the deep perft counts, which take a few minutes.

## Settings

The app is **not** configured from the environment. Its settings are a YAML file
inside the deployable, parsed into a dataclass. `.env` here holds test switches
only; copy `.env.example` to `.env` if you want them.

To run a container with different app settings, mount your own file over the
one the image ships with — `/app/deployables/chess-cli/config/chess_cli.yaml`,
`/app/deployables/fastapi-gateway/config/fastapi_gateway.yaml` — or pass
`--config /some/path.yaml` after the command.

## Build context

The context is the repository root, not this directory: `chess-cli` reaches
`chess-game` through a relative path and both trees must be present, and the
root `.dockerignore` keeps the context small for every image built from it.
