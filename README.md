# board-gamez

An online multiplayer board-game platform. People sit at tables, take seats, and
play a game the platform hosts without interpreting its rules.

## Running the stack locally

Needs Docker. Builds any missing image, then starts everything detached: the
store, the gRPC server on 50051, the gateway on 8080 and the interface on 8081.

```bash
./infra/scripts/up.sh              # everything, in the background
./infra/scripts/down.sh            # stop and remove every container
```

Check that both answer:

```bash
curl http://127.0.0.1:8080/openapi.json          # the gateway's paths
grpcurl -plaintext 127.0.0.1:50051 list          # the server's services
```

## Playing in a browser

The interface is [`deployables/gamez-ux`](deployables/gamez-ux/). Nothing has to
be installed: the node toolchain is a container, and `up.sh` serves it on 8081.

Or against a backend already running on this machine:

```bash
./deployables/gamez-ux/scripts/local-dev.sh     # on 5173
```

**Every browser tab is a different player.** There is no sign-in yet, so open a
second tab to take the seat opposite yourself.

Which gateway it calls, which theme it wears and how often it polls are in
[`deployables/gamez-ux/config/gamez_ux.json`](deployables/gamez-ux/config/gamez_ux.json).

Run the checks the same way CI does:

```bash
./infra/scripts/test.sh
./infra/scripts/lint.sh
```

## Architecture

The layers, and which one a given file belongs to, are in
[ARCHITECTURE.md](ARCHITECTURE.md). Read it before adding code.

```
Presentation → Application → Business → Persistence → Database
               deployables/   controller/  repository/   Redis
               service/                                  infra/
```

Adapters sit between layers, in `<domain>/adapters/`.

```
setup.sh                       prepare this machine — idempotent, safe to re-run
ARCHITECTURE.md                the layers, and which one a file belongs to
.pre-commit-config.yaml        what has to pass before a commit lands, and a push
.claude/skills/python-style/   the house style, loaded before any .py is written
.claude/skills/modeling/       how the system is modelled, loaded before any .proto
.claude/skills/backend-development/  the layers, loaded before adding a component
idl/contracts/                 the schema every layer shares, and what it generates
packages/chess/                the chess engine — rules only, no input or output
packages/lobby/                tables and seats — rules only, in the schema's own types
deployables/chess-cli/         the terminal game — owns its environment and its config
deployables/fastapi-gateway/   the HTTP gateway — owns its environment and its config
infra/                         compose files and the scripts that drive them
```

## Getting set up

```bash
./setup.sh                  # uv, the Python environments, then verify
./setup.sh --with-docker    # also install Docker Engine (needs sudo)
```

Every step checks its target state before acting, so running it twice does what
running it once did. It never removes or overwrites anything you already have.

## Playing

```bash
./deployables/chess-cli/scripts/local-play.sh   # on this machine
./infra/scripts/play.sh                         # in a container
```

## Serving

```bash
./deployables/fastapi-gateway/scripts/local-serve.sh   # on this machine
./infra/scripts/serve.sh                               # in a container
```

The gateway carries no routes yet; it answers `/openapi.json` and `/docs` with
the title and version its config file names.

## The shared vocabulary

A chess position means the same thing in the engine, in a browser and in an
OpenAPI document because all three are generated from one schema.

```bash
./idl/scripts/generate.sh   # rewrite idl/contracts/gen from idl/contracts/proto
./idl/scripts/check.sh      # lint, format, regenerate, and refuse any drift
```

`idl/contracts/gen` is committed, so a consumer needs the schema and not the
toolchain. See [idl/README.md](idl/README.md).

## Layout rules

- **A package is a library.** No I/O, no configuration, no terminal knowledge.
  `packages/chess` has zero dependencies and never prints.
- **A deployable is an app.** It owns its Dockerfile, its entrypoint, its
  dependency set and its `config/`. Nothing has to be installed on the host.
- **An app is brought up from a YAML file** parsed into a dataclass by a
  mashumaro mixin. Nothing reads the environment.
- **Swappable collaborators go through a provider.** A display or a console is a
  `config.py` / `base_*.py` / concrete / `provider.py` package, selected by
  configuration; consumers are typed against the base class only.
- **One schema, many languages.** Anything that crosses a process boundary is
  described once in `idl/contracts/proto` and generated into
  `idl/contracts/gen`. The generated types are the wire; `packages/chess` keeps
  its own models, because those carry behaviour a generated class cannot.
  Converting between them is an adapter.
- **Dependencies point one way**: `deployable → package → models`.
- **There is no workspace root.** Each `pyproject.toml` stands alone; a deployable
  reaches a package through a relative `[tool.uv.sources]` path. Python 3.13 is
  pinned by `requires-python`, not by a `.python-version` file.

## Style

Every Python file here is written against
[.claude/skills/python-style/SKILL.md](.claude/skills/python-style/SKILL.md). The
parts a machine can check — no `from __future__ import annotations`, no
function-level imports, no magic values, no `Any` — are enforced by the ruff and
mypy settings in each `pyproject.toml`, not by good intentions.

`setup.sh` wires those checks into git, so they run without being remembered:
ruff lints and formats what you commit, and mypy type-checks every project the
commit touches. Ruff finds its settings by walking up from each file, so a commit
spanning two projects is judged by each project's own rules — there is still no
workspace root.

```bash
pre-commit run --all-files              # check the whole tree now
git commit --no-verify                  # land it anyway, just this once
```

The container linter runs the same two ruff commands (`./infra/scripts/lint.sh`),
so a green pipeline and a green commit mean the same thing.
