# chess-cli

A two-player chess game for the terminal. Owns its environment and its settings:
the image, the entrypoint, the dependency set and the config file all live here.

## Layout

```
config/       the YAML the app is brought up from
docker/       Dockerfile and the entrypoint that knows how to run anything
scripts/      running on this machine, without a container
src_python/   main.py, plus the chess_cli package
tests/        the CLI's own tests, driven through a scripted console
```

```
chess_cli/
├── cli_settings.py     the settings type — the only reader of the config file
├── config_error.py
├── command*.py         turning a typed line into a Command
├── terminal_game.py    the prompt loop
├── display/            how the game is shown
└── console/            where input and output go
```

The engine knows nothing about terminals; everything here is presentation.

## Swappable pieces

Both `display/` and `console/` follow the same four-file shape, and the game loop
is typed against the base classes only — it cannot name a concrete display or
console, so it cannot grow a dependency on one.

```
display/
├── config.py         DisplayType enum + TextDisplayConfig + DisplayConfig
├── base_display.py   BaseDisplay
├── text_display.py   the concrete text implementation
└── provider.py       DisplayProvider.get_display(config) -> BaseDisplay
```

Adding a display is purely additive: an enum member, a config dataclass, a field
on `DisplayConfig`, a module and a registry entry. Nothing existing changes.

`main.py` builds both from configuration, once, and passes them in.

## Settings

Brought up from `config/chess_cli.yaml`, parsed into `CliSettings` by a mashumaro
YAML mixin. **Nothing in this app reads the environment.**

```yaml
players:
  white_name: White
  black_name: Black
display:
  display: text
  text_config:
    use_unicode: true
    show_coordinates: true
console:
  console: terminal
  terminal_config:
    prompt_suffix: "> "
```

Run with different settings by pointing at another file:

```bash
scripts/local-play.sh --config /path/to/your.yaml
```

A missing file, a missing field, a malformed document, or a display selected with
no matching config section all stop the app with a message naming the problem.

## Running

On this machine (needs `uv` — run `./setup.sh` at the repository root):

```bash
scripts/local-play.sh
scripts/local-test.sh
scripts/lock.sh          # rewrite uv.lock using uv inside a container
```

In a container, from [infra/](../../infra/):

```bash
../../infra/scripts/play.sh
../../infra/scripts/test.sh
../../infra/scripts/lint.sh
```

## Commands at the prompt

Moves are typed as the square you leave and the square you reach — `e2e4` — with
the new piece appended for a promotion: `e7e8q`. Coordinates go in; the move list
comes back in algebraic notation (`Nf3`, `exd5`, `O-O`, `Qxf7#`).

`moves` `board` `history` `undo` `resign` `help` `quit`
