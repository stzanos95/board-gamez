# board-gamez

Games, one package per game engine and one deployable per way of playing it.

```
setup.sh                       prepare this machine — idempotent, safe to re-run
.pre-commit-config.yaml        what has to pass before a commit lands, and a push
.claude/skills/python-style/   the house style, loaded before any .py is written
.claude/skills/modeling/       how the system is modelled, loaded before any .proto
idl/contracts/                 the schema every layer shares, and what it generates
packages/chess/                the chess engine — rules only, no input or output
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
ruff lints and formats what you commit, and mypy type-checks both projects before
a push leaves the machine. Ruff finds its settings by walking up from each file,
so a commit spanning both projects is judged by each project's own rules — there
is still no workspace root.

```bash
pre-commit run --all-files              # check the whole tree now
pre-commit run --all-files --hook-stage pre-push   # ...including the type checks
git commit --no-verify                  # land it anyway, just this once
```

The container linter runs the same two ruff commands (`./infra/scripts/lint.sh`),
so a green pipeline and a green commit mean the same thing.
