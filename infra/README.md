# infra

Everything that lifts a deployable into a container.

```
compose/     the compose files
scripts/     thin wrappers over them, runnable from anywhere
.env.example test switches only — app settings live in the deployable's config/
```

## Scripts

```bash
scripts/build.sh    build the chess-cli image
scripts/play.sh     play a game
scripts/dev.sh      play with the host source bind-mounted, no rebuild needed
scripts/test.sh     both test suites
scripts/lint.sh     ruff and mypy
```

`play.sh` uses `docker compose run`, not `up` — an interactive prompt needs stdin
attached, which `up` does not do.

`dev.sh` bind-mounts `packages/` and `deployables/` read-only. Safe because the
virtualenv lives at `/opt/venv`, outside the mounted trees. Editing
`deployables/chess-cli/config/chess_cli.yaml` takes effect on the next run.

`CHESS_SLOW_TESTS=1` adds the deep perft counts, which take a few minutes.

## Settings

The app is **not** configured from the environment. Its settings are a YAML file
inside the deployable, parsed into a dataclass. `.env` here holds test switches
only; copy `.env.example` to `.env` if you want them.

To run the container with different app settings, mount your own file over
`/app/deployables/chess-cli/config/chess_cli.yaml`, or pass
`--config /some/path.yaml` after the command.

## Build context

The context is the repository root, not this directory, because `chess-cli`
reaches `chess-game` through a relative path and both trees must be present.
`.dockerignore` at the root keeps the context small.
