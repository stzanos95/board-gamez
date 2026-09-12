# idl

The vocabulary every layer shares, written once.

```
contracts/
├── proto/    the schema — the only thing here written by hand
└── gen/      what the schema compiles to, one directory per language
third_party/  protos vendored from googleapis, so generation needs no network
scripts/      thin wrappers over the toolchain, runnable from anywhere
  templates/  the packaging that ships beside the generated code
docker/       the toolchain itself: protoc, its plugins, and buf
buf.yaml      what counts as a well-formed schema
```

`contracts/` is what other layers consume. Everything beside it exists to produce
`contracts/gen` from `contracts/proto` and to keep the two honest, and nothing
outside this directory should ever need to know it is here.

A chess position means the same thing in the engine, in a browser and in an
OpenAPI document because all three are generated from `contracts/proto`. When the
two sides of a boundary each declare their own idea of a `Move`, they agree until
the day one of them is edited.

## The schema

One directory per domain, and inside it one directory per job a message can have.

```
contracts/proto/idl/
├── core/      what every domain needs and no domain owns
│   ├── dto/       the envelopes a socket frame and a queue message travel in
│   └── obj/       the metadata every stored row carries
├── identity/  who someone is
│   └── model/
├── lobby/     where people gather to play
│   ├── model/     tables, seats, the choices a game offers, and what happened at a table
│   ├── dto/       what TableService, SeatService and SeatingService carry
│   ├── obj/       a stored table
│   └── service/   TableService (the store), SeatService (the verbs), and SeatingService — implemented once per game
├── game/      a game being played, whatever game it is
│   ├── model/     a session, a state, an action, a result, and what happened in a game
│   ├── dto/       what SessionService, GameSpecService and RulesService carry
│   ├── obj/       a stored session
│   └── service/   SessionService, GameSpecService, and RulesService — implemented once per game
└── chess/     one game
    ├── model/     the rules' vocabulary, a seat's side, and a game or a table as one viewer sees it
    ├── dto/       what ChessService takes and hands out
    └── service/   ChessService — chess as a browser sits down to it and plays it
```

`game` never imports `chess`. A game's state and actions reach the session layer
packed into `google.protobuf.Any`, stored and relayed without being opened, which
is what lets one server host every game. A seat's role — the side it plays, the
token it moves — reaches the lobby the same way. Adding a game is a `GameType`
member and one implementation each of `RulesService` and `SeatingService`.

Every write that succeeds is one event in `<domain>/model/event.proto`, in that
domain's vocabulary and with the version after the write. Events are published
inside `core.dto.QueueMessageEnvelope` under the event's full type name, and are
the backend's own: a browser is sent only the `*Changed` message at the end of
each file, which carries an id and a version and nothing else.

`chess` imports `game`: its service answers the platform's outcomes, and its
session is the platform's session with the game opened. The dependency runs from
the specific domain to the generic one and never the other way.

The `idl/` segment above them is the Python import root, and it earns its place
for that reason alone — see below.

The split is what keeps one change from becoming three. A stored row gains an
index, an API response gains a field a client asked for, and neither reaches into
the rules. What belongs in each is in `.claude/skills/modeling/`.

Every chess type is the schema's. `packages/chess` computes over
`idl.chess.model` messages and enums — a square, a move, a position key, a
turn — and declares no type of its own for anything the schema names. What it
adds is behaviour: a board indexed by square, the pieces that generate moves,
and static lookups over the schema's values.

## Generating

```bash
./idl/scripts/generate.sh              # rewrite every target in contracts/gen
./idl/scripts/generate.sh typescript   # or one: python, typescript, openapi, fastapi
./idl/scripts/lint.sh                  # naming, enum zero values, RPC shapes
./idl/scripts/breaking.sh              # refuse a change that breaks a client on main
./idl/scripts/check.sh                 # all of the above, in the order worth knowing
```

Nothing has to be installed on this machine. The toolchain is a container, and
every script builds it when the Dockerfile has changed under it — bumping a
pinned version needs no one to remember to rebuild.

The targets are generated in order and a failing one stops the run, so the
targets after it write nothing. Name a single target to see its errors on their
own; an empty output directory beside a populated one is the sign.

**`contracts/gen` is committed, and never edited.** A consumer needs the schema,
not the toolchain — a browser project pulls `contracts/gen/typescript` without
knowing protoc exists. `check.sh` regenerates and fails if the result differs, so
the committed output cannot quietly drift from the schema.

Each output directory is emptied before it is written. A message deleted from a
`.proto` does not leave its generated class behind, still importable and now a
lie.

## Targets

| Directory                  | Produced by           | What a consumer needs                      |
| -------------------------- | --------------------- | ------------------------------------------ |
| `contracts/gen/python`     | `protoc --python_out` | `protobuf` — installable, see below        |
| `contracts/gen/typescript` | `protoc-gen-es`       | `@bufbuild/protobuf`                       |
| `contracts/gen/openapi`    | `protoc-gen-openapi`  | nothing — it is a document                 |
| `contracts/gen/fastapi`    | `datamodel-codegen` + `render_routers.py` | `fastapi`, `pydantic` |

### FastAPI

Generated from the OpenAPI document rather than from the `.proto` files, so it
runs after the `openapi` target. An installable distribution, like the Python
one:

```
contracts/gen/fastapi/
├── pyproject.toml                  rendered from scripts/templates/
└── src/idl_fastapi/
    ├── idl/lobby/model.py          one module per proto package
    └── services/table_service.py   one module per service
```

Each service module holds an abstract base declaring one method per operation,
and a router class binding every path to an instance of it:

```python
class LobbyRouters:
    @staticmethod
    def table_service() -> APIRouter:
        return TableServiceRouter.build(TableServiceBinding())
```

The generated modules hold no behaviour, so an implementation never lives in
this tree: a domain package implements the base, and a deployable includes the
router. Regenerating cannot overwrite either.

Three choices in `docker/entrypoint.sh` are load-bearing. Schema names are fully
qualified, so two domains may both declare a `Table`. Enum fields are `Literal`
rather than `Enum` classes, because a proto enum is inlined into the field
carrying it — the generator would name a class after that field and number the
duplicates, so adding a message could renumber a class every consumer imports by
name. And the formatter is `builtin` with no timestamp, so regenerating an
unchanged schema produces an unchanged file.

Its own root package: the Python target already publishes a top-level `idl`, and
two distributions cannot both own that name.

### Python

An installable distribution, packaging included:

```
contracts/gen/python/
├── pyproject.toml        rendered from scripts/templates/
└── src/idl/chess/model/  protoc's output
```

A consumer depends on it the way `packages/product-chess` depends on
`packages/chess` — a relative path, no workspace, nothing published anywhere:

```toml
[project]
dependencies = ["board-gamez-idl"]

[tool.uv.sources]
board-gamez-idl = { path = "../../idl/contracts/gen/python", editable = true }
```

```python
from idl.chess.model.board_pb2 import BoardState
from idl.chess.model.piece_pb2 import Color, PieceType
```

Editable, so regenerating the schema reaches the consumer without a reinstall.

**Why the schema has an `idl/` directory in it.** protoc derives a generated
module's import path from the `.proto` file's own path, and writes that path into
every generated import. `idl.chess.model` is therefore only reachable if the
protos live under an `idl/` segment — no amount of packaging can rename the root
after the fact. That segment also keeps this tree from colliding with the
top-level `chess` package that `packages/chess` publishes, which two regular
packages of one name on a `sys.path` would do, the first found winning and the
other disappearing.

**The protobuf floor is read, not written down.** protoc stamps the runtime it
targets into the header of every module it writes, and those modules refuse to
import under anything older. The generator reads it back out and renders it into
the dependency, so bumping `PROTOC_VERSION` in `docker/Dockerfile` moves the
floor with it and there is no second place to remember.

A `py.typed` marker is written beside the generated packages, so a consumer's
mypy reads the `.pyi` stubs rather than treating the distribution as untyped.
Verified under `--strict --disallow-any-explicit`.

`google/api` is not generated for Python. It would put a top-level `google`
package on `sys.path` that shadows the real one, and `import google.protobuf`
would stop working. When a service proto needs those two modules, they come from
the `googleapis-common-protos` wheel.

### TypeScript

The same shape, with `package.json` in place of `pyproject.toml`:

```
contracts/gen/typescript/
├── package.json          rendered from scripts/templates/
└── src/
    ├── idl/chess/model/  protoc's output
    └── google/api/       generated here, unlike for Python
```

The export map drops the `idl/` segment that Python needs, because the package
name already carries it, and names `google/` separately because it sits beside
`idl/` rather than inside it:

```json
{ "exports": { "./google/*": "./src/google/*.ts", "./*": "./src/idl/*.ts" } }
```

The `.ts` is in the target rather than in the specifier. An export pattern
resolves to a file and nothing adds an extension to it, so a map without one
answers with a path that does not exist and every import of this package fails.

```ts
import { BoardState } from "@board-gamez/idl/chess/model/board_pb";
import { http } from "@board-gamez/idl/google/api/annotations_pb";
```

The `http` extension is what carries a method's HTTP path. A client reads the
path off the service descriptor rather than declaring it, so the URL an
operation is served at is stated once, in the `.proto` that declares the
operation.

**It ships TypeScript source, not compiled JavaScript.** A consumer therefore
bundles or compiles it, which is the normal arrangement for a package inside one
repository and the reason there is no `tsc` in the toolchain image — adding one
would mean an `npm install` on the generate path, and generation deliberately
touches no network. Publishing this to a registry is what would make a build step
worth its cost.

Imports between generated files carry no extension, so a consumer wants
`"moduleResolution": "bundler"`.

The `@bufbuild/protobuf` dependency is the version of `protoc-gen-es` that wrote
the code — they are one release, and the generator renders the image's own pin
into the package.

### OpenAPI

`protoc-gen-openapi` walks services, not messages. A service without
`google.api.http` annotations contributes no paths; `RulesService` is one, since
nothing outside the platform asks a game for its rules.

### Why every file declares a Go package

`option go_package` is on all six model files, and Go is not a target.

`protoc-gen-openapi` is a Go program built on `protogen`, which refuses to run
against a file that does not name a Go import path — it has no way to know the
caller does not want Go out the other end. Declaring it in the schema fixes it
for every Go-based plugin at once, which is why it is here rather than as a
sheaf of `M` flags in `entrypoint.sh` that the next such plugin would need again.

The path is a placeholder: `boardgamez/contracts/gen/go/...`, no host, nothing
resolves it. Point it at a real module when Go becomes a target.

### gRPC

Service stubs are not generated. Adding them means pinning one more plugin in
`docker/Dockerfile`.

## Rules

- **`contracts/proto` is the source of truth.** Not the Python dataclasses, not a
  TypeScript interface someone wrote by hand. If the two disagree, the schema is
  right.
- **A type the schema declares is not declared again.** A Python enum or
  dataclass that mirrors a message is a second definition that drifts. The
  engine holds the generated type and puts behaviour beside it, in a class of
  static methods: `Colors.opponent(color)`, `Squares.shifted(square, vector)`,
  `GameStatuses.is_terminal(status)`. A message is not hashable, so a lookup
  keyed by one uses an index computed from it (`Squares.get_index`); nothing
  else about it differs. The one conversion left is shape: a board indexed by
  square from the schema's list of occupied squares, and back.
- **Never renumber a field, and never reuse a number.** Deleting one means
  `reserved 4;`, so a client on the old schema cannot silently read a new field
  as an old one. `breaking.sh` is what enforces this.
- **A breaking change is a new directory.** `chess/model/v2` lives beside
  `chess/model` until nothing speaks the old one any more. The version is not in
  the package name today, and `buf.yaml` turns off the rule that asks for it;
  turn it back on when the first v2 arrives.
- **Enums start at `_UNSPECIFIED`.** proto3 requires a zero value, and it is what
  a consumer sees when reading a field a newer schema has not set. No producer
  writes it.

## Adding a message

1. Write it in the right file under `contracts/proto/idl/chess/model/`, or add one.
2. `./idl/scripts/lint.sh`.
3. `./idl/scripts/generate.sh`.
4. Commit `contracts/proto` and `contracts/gen` together. They are one change.

## Toolchain

Every version is pinned in the `ARG` block at the top of `docker/Dockerfile`,
which is the only place to bump one. An unpinned toolchain generates different
code on different days, which is the one thing generated code must never do.

Generation is driven by `protoc` rather than `buf generate`: all three targets
are plain protoc plugins, and `docker/entrypoint.sh` says exactly what each one
receives. buf owns linting and breaking-change detection, which it does better
than anything else.
