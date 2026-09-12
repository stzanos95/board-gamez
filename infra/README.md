# infra

Everything that lifts a deployable into a container.

```
compose/     the compose files
scripts/     thin wrappers over them, runnable from anywhere
```

## Scripts

```bash
scripts/build.sh    build every deployable's image
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
effect on the next run. It runs `fastapi-gateway` unless another service is
named: `scripts/dev.sh grpc-server`.

## Settings

An app is **not** configured from the environment. Its settings are a YAML file
inside the deployable, parsed into a dataclass.

To run a container with different app settings, mount your own file over the
one the image ships with — `/app/deployables/fastapi-gateway/config/fastapi_gateway.yaml`,
`/app/deployables/grpc-server/config/grpc_server.yaml` — or pass
`--config /some/path.yaml` after the command.

## Build context

The context is the repository root, not this directory: a deployable reaches
the packages it depends on through relative paths, so every tree must be
present, and the root `.dockerignore` keeps the context small for every image
built from it.
