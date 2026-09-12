---
name: python-style
description: Coding standards for ALL Python in this repository. Load before writing or editing any .py file — domain models, services, entry points, config, adapters, or throwaway scripts. Covers import rules (no `from __future__ import annotations`, no function-level imports, empty `__init__.py`), banning magic strings/numbers, modelling domain vocabulary as dataclasses and enums, bringing every app up from a YAML config parsed by a mashumaro dataclass mixin rather than the environment, and how SOLID and clean-code apply here.
---

# Python style

Non-negotiables first — these are absolute and have no exceptions.

## 1. Imports

**Never `from __future__ import annotations`.** Annotations must stay real runtime
objects. Anything that introspects them at runtime reads them as objects, and the
future import turns every one of them into a string. This is not hypothetical
here: mashumaro reads the annotations on every settings dataclass to generate its
YAML parser (rule 4), and the dataclass machinery itself reads them to build
`__init__`. For a self-reference use a string forward ref: `-> "ChessBoardState"`.

**Every import at module top.** No imports inside a function, method, class body,
or `if TYPE_CHECKING:` block. If a type is only needed for an annotation and
importing it is awkward, leave the parameter unannotated with a short comment —
do not add a deferred import.

**`__init__.py` files stay empty.** No re-exports, no convenience imports.
Consumers use the full path:

```python
from chess.pieces.bishop import Bishop              # yes
from chess.models.square import Square                 # yes
from chess import Bishop                            # no — __init__ must be empty
```

A circular import between packages is a design signal, not an import problem.
Fix it by moving the shared thing down into the lowest layer — never by deferring
an import.

The worked example is this repo's own. `BasePiece` needs to read the board, and
the board holds pieces; naively that is a cycle. It is not, because
`BoardStateView.occupant()` hands back an `Occupant` — a small frozen record of colour
and piece type — rather than a `BasePiece`. Pieces never need the object, only
whose-and-what, so the shared thing moved down into `models` and the cycle
disappeared.

## 2. No magic strings or numbers

A bare literal that carries meaning gets a name. In practice:

- **Closed sets of values → an enum in its own module.** `LogLevel`,
  `DisplayType`, `SeatOutcome` — one enum per file, never nested inside another
  class (nesting forces callers to import the container just to read the enum).
  A closed set the schema declares (`Color`, `PieceType`, `GameStatus`) is the
  generated enum and is never declared again; see rule 3.
- **An enum's base class is its value type.** `StrEnum` when the values are
  strings, `IntEnum` when they are integers, plain `Enum` when they are neither.
- **Tuning values → a module constant.** `BOARD_SIZE = 8`,
  `MAX_HALFMOVE_CLOCK = 100`.
- **Values that vary by input → a lookup function, not an inline default.**
  `pawn_direction(color)` exists because hardcoding a forward step of `+1`
  silently produces a board where Black's pawns march the wrong way.
- **Deployment values → config, never literals.** Hosts, ports, names and
  feature switches come from the YAML configuration file, through a frozen
  settings dataclass (rule 4).

```python
size = BOARD_SIZE                    # yes
size = 8                             # no
```

The exception is a literal whose meaning is fully local and obvious — `range(2)`,
`text.strip()`, an index `[0]` right after the thing it indexes.

### Which enum base

```python
class LogLevel(StrEnum):             # yes — the values are strings
    INFO = "info"

class File(IntEnum):                 # yes — the values are indices
    A = 0

class Direction(Enum):               # yes — a Vector is neither
    NORTH = Vector(file_delta=0, rank_delta=1)

class LogLevel(Enum):                # no  — a str value, so StrEnum
    INFO = "info"
```

A `StrEnum` member **is** the string and an `IntEnum` member **is** the number.
The member serialises as its value, formats as its value, and is accepted
wherever the underlying type is: `f"{level}"` is `info`, and a library that takes
a `str` takes the member itself. Nothing has to remember to write `.value`.

Two consequences come with that, and both are the price of the value being real:

- **An `IntEnum` member whose value is `0` is falsy.** Write `if file is None`,
  never `if not file`.
- **Members compare equal to bare values**, so `Color.WHITE == "white"` is
  `True`. An equality test meant to catch a typo no longer catches one. Compare
  members with `is`, and keep the enum on both sides.

## 3. Model domain vocabulary as types

**When a domain has its own nouns, those nouns become classes.** Anything passed
between layers — function returns, internal exchanges, computed results — is a
`@dataclass`, never a bare `dict`, `tuple`, or positional pair.

**A noun the schema already names is the generated type.** `Square`, `Move`,
`CastlingRights`, `Color` are `idl.chess.model`'s messages and enums, held and
computed over as they are. A dataclass or enum mirroring one is a second
definition that drifts, and it makes the engine harder to reimplement against
the same schema in another language. Behaviour goes beside the type in a class
of static methods, named for the plural of the noun: `Colors.opponent(color)`,
`Squares.shifted(square, vector)`, `MoveTypes.is_capture(move_type)`,
`CastlingRightSets.allows(rights, color, side)`. A message is not hashable, so
a lookup keyed by one uses an index computed from it (`Squares.get_index`).
Enum values are integers: compare them with `==`, never `is`.

What stays a Python type is what the schema has no reason to name: a board
indexed by square, a piece that generates moves, a displacement vector.

```python
# no — which one is the origin? two same-typed values, and a transposition
# quietly moves the piece backwards
def generate(...) -> list[tuple[Square, Square]]: ...

# yes
@dataclass(frozen=True, slots=True)
class Move:
    origin: Square
    destination: Square
```

**What is banned is a container standing in for a record** — one whose positions
or keys carry the meaning, so that reading it correctly depends on remembering an
order or a spelling. A container holding many of one already-named type is a
collection, and stays a plain container:

```python
def moves_for_side_to_move(...) -> tuple[Move, ...]: ...   # yes — a collection
def attacked_squares(...) -> frozenset[Square]: ...        # yes — a collection
def generate(...) -> list[tuple[Square, Square]]: ...      # no  — a record
def summarise(...) -> dict[str, list[str]]: ...            # no  — a record
```

The test: if you had to write a comment to say what a position or key means, it
is a record and wants a class. If every element is the same named type and the
order carries nothing, it is a collection.

### Shape

- **`frozen=True, slots=True` by default.** Computed results are snapshots, not
  live views. Drop `frozen` only when a value is genuinely drawn down as it is
  processed, and say so in the docstring.
- **New object over mutation.** Transform by constructing, not by reassigning
  fields on something a caller still holds. `piece.relocated_to(square)` returns
  a new piece; it does not move the one you passed in. Where mutation is
  unavoidable — a local accumulator — keep it inside one function and never hand
  a half-updated object across a boundary.
- **Named entities over loosely shaped containers.** A thing with a name and
  fields beats a `dict`, a tuple, a `SimpleNamespace`, or "a list of 3-tuples".
  If you catch yourself writing a comment to explain a structure's shape, that
  comment wants to be a class.
- **Explicit field names and explicit ownership.** `file_delta` / `rank_delta`,
  not `a` / `b` or positional order. Every field says what it is.

### Typing

- **Annotate every parameter and every return.** No bare `list`, `set`, `dict`,
  or omitted parameter types — `-> tuple[Move, ...]`, not `-> tuple`;
  `square: Square`, not `square`.
- **Never `Any`.** If a type is hard to name, that is a design signal: name the
  concept instead. The only tolerated gaps are third-party objects with no
  usable type (leave the parameter unannotated with a comment rather than
  importing something just to satisfy a checker).
- **Type aliases for domain identifiers and quantities**, defined once in the
  lowest layer. An alias reads as a domain fact where the underlying builtin
  reads as a storage detail.
- **Simple return types.** Return one named thing. Prefer `GameResult` over
  `dict[str, list[tuple[str, int]]]`, and a `tuple[Move, ...]` over a nested
  `dict[str, dict[str, list[Move]]]`. If a function wants to return three loosely
  related values, it is probably two functions — or the three values are a type
  you have not named yet.

### `dict` is for lookups, not for records

A `dict` is legitimate when the keys are *data* — a caller-supplied mapping, a
square→piece index that is genuinely iterated by key. It is never the right way
to carry a fixed set of known fields. Assembling
`{"status": ..., "winner": ...}` to hand back from a function means the
dataclass is missing.

Where a `dict` is the right answer, **name its shape with a type alias**, defined
once in the lowest layer that knows both sides, and use the alias wherever the
mapping is built or held:

```python
RulesByGameType = dict[GameType, BaseRules]                  # yes

self._rules: RulesByGameType = {}                            # yes
# Keys are data — a game type names the rules that play it.
self._rules: dict[GameType, BaseRules] = {}                  # no — a comment where a name belongs
```

The alias is what says the keys are data. A comment saying so is noise that has
to be repeated at every dict.

### Third-party shapes get modelled too

**"The library wants a nested dict" is not an exemption.** A framework's expected
mapping is still a fixed set of known fields. Left as a literal, the shape is
documented only by that literal, every key is an unchecked string, and the
library's magic values are scattered through assembly code.

Model the contract in **its own module, named for the thing**, holding the
constants, enums and frozen dataclasses that describe it — and the conversion:

```python
# api/report_backend_settings.py — models the mapping a reporting library wants
BACKEND_ID = "tabular"                      # the library's magic values become
COMPRESSION_NONE = "none"                   # named constants, once, here

@dataclass(frozen=True, slots=True)
class ReportBackendSettings:
    backend_id: str
    columns: list[str]
    compression: str

    @staticmethod
    def from_config(report: ReportConfig) -> "ReportBackendSettings": ...

    def to_dict(self) -> dict[str, object]:   # the ONE place it becomes a mapping
        return {"BACKEND": self.backend_id, "COLUMNS": self.columns, ...}
```

- **Encode/decode lives in that file and nowhere else.** `from_*` to build,
  `to_dict()` to emit. No other module constructs the literal.
- **The library's magic values become named constants** — variable names, mode
  strings, dotted paths.
- **Prefer explicit keyword arguments to splatting** where the callee accepts
  them: every value stays visible at the call site; `**mapping` hides them.
- **The outer container may stay a dict when its keys are genuinely data.** Say
  so in the docstring.

Test: if you cannot point at one file that fully describes the shape an outside
system expects, it is not modelled yet.

Put meaning-bearing behaviour in one place: `GameStatuses.is_terminal(status)`
beats `status in (GAME_STATUS_CHECKMATE, GAME_STATUS_STALEMATE, ...)` at every
call site.

## 4. Configuration is a file parsed into a dataclass

**Every app is brought up from a YAML file.** Not from `os.environ`, not from
`os.getenv`, not from argparse defaults standing in for settings, not from
constants edited before a deploy. One file, parsed once, into one type.

**The settings type is a frozen dataclass with a mashumaro YAML mixin:**

```python
# grpc_server/service_host_config.py
from dataclasses import dataclass
from pathlib import Path

from mashumaro.mixins.yaml import DataClassYAMLMixin


@dataclass(frozen=True, slots=True)
class ServerConfig(DataClassYAMLMixin):
    host: str
    port: int


@dataclass(frozen=True, slots=True)
class ServiceHostConfig(DataClassYAMLMixin):
    application: ApplicationConfig
    server: ServerConfig
    lobby: LobbyConfig

    @staticmethod
    def from_yaml_file(path: Path) -> "ServiceHostConfig": ...

    def to_yaml_file(self, path: Path) -> None: ...
```

- **One settings module per app, and it is the only place a config file is read
  or written.** `from_yaml_file` to bring up, `to_yaml_file` to emit. No other
  module opens the file, and no other module reads a setting from anywhere else.
- **Group settings into nested dataclasses that name a concern** — `server`,
  `lobby` — rather than one flat bag of twenty fields.
- **The entry point takes a path and nothing else.** `--config <path>`, with a
  default beside the app. The path is the only thing the outside world gets to
  say.
- **The config file lives in the app's own `config/` directory** and is version
  controlled. It documents what the app needs as much as it feeds it.
- **Refuse bad configuration loudly.** A missing file, a missing field or a
  malformed document stops the app with a message naming the path and the
  problem. A setting that silently falls back to a default when it was misspelled
  is a bug that only ever surfaces in production.
- **The environment is not configuration.** A container may pass a *path* to a
  config file; it must never pass the settings themselves. A switch that selects
  which tests run configures the harness, not the app, and is the one thing that
  may stay an environment variable.

Settings in a file can be read, reviewed, diffed and version controlled as one
object, and they have types before anything runs. Settings scattered across
environment variables are discoverable only by grepping for variable names and
hoping you found them all.

## 5. SOLID, as it applies here

- **Single responsibility** — one writer per invariant. `ChessBoardState` is the
  *only* thing that produces board state, because it is what guarantees the
  occupancy map, castling rights and clocks stay consistent with each other. A
  second write path is a bug, not a convenience.
- **Open/closed** — extend by adding a type, not by editing an existing one. A
  new piece is a new `BasePiece` subclass; nothing else changes. Reach for this
  shape whenever you feel like adding a branch to a growing `if/elif`.
- **Liskov** — an abstract base's subclasses must be substitutable. Every
  `BasePiece` answers `pseudo_legal_moves` and `attacked_squares` with the same
  meaning; the generator never asks what concrete class it holds.
- **Interface segregation** — expose only what a caller needs. Pieces receive
  `BoardStateView`, not `ChessBoardState`: they can read occupancy and cannot reach the
  mutation surface at all.
- **Dependency inversion** — see below. Depend on the lower contracts layer,
  never sideways on a peer. Layering runs `deployable → domain package → models`,
  one direction only.

### Dependency inversion, concretely

**Where an app has a choice to make — which store it writes to, which client
it calls through — that choice is a package of four files and nothing else:**

```
<thing>/
├── config.py            the enum that selects, and one config dataclass per option
├── base_<thing>.py      the abstract base every option implements
├── <option>_<thing>.py  one concrete implementation per file
└── provider.py          a registry, and a static factory that selects by config
```

`config.py` is the one place an enum shares a module with other types, because
the enum and the configs are a single contract: the enum says which, and each
config says what that one needs. Splitting them leaves a reader holding the
selector with no way to see what selecting it implies. The container carries one
optional field per option:

```python
class TableRepositoryType(StrEnum):
    REDIS = "redis"

@dataclass(frozen=True, slots=True)
class RedisTableRepositoryConfig(DataClassYAMLMixin):
    host: str
    port: int

@dataclass(frozen=True, slots=True)
class TableRepositoryConfig(DataClassYAMLMixin):
    repository: TableRepositoryType
    redis_config: RedisTableRepositoryConfig | None = None
```

`provider.py` is a registry and a static factory, never a chain of `if`s. The
registry is a `ClassVar` on the provider, declared after the builders it
names, so the class is the whole contract and nothing about it sits at module
level:

```python
class TableRepositoryProvider:
    @staticmethod
    def get_table_repository(config: TableRepositoryConfig) -> BaseTableRepository:
        builder = TableRepositoryProvider.BUILDERS_BY_TYPE.get(config.repository)
        ...

    @staticmethod
    def _build_redis_table_repository(config: TableRepositoryConfig) -> BaseTableRepository: ...

    BUILDERS_BY_TYPE: ClassVar[
        dict[TableRepositoryType, Callable[[TableRepositoryConfig], BaseTableRepository]]
    ] = {
        TableRepositoryType.REDIS: _build_redis_table_repository,
    }
```

A staticmethod object is callable in the class body, so the registry names the
builder directly. When one selection builds more than one thing — a queue's
publisher and consumer — it is one registry per thing, each on the class.

When an option has a directory of its own, the directory is named for the
option and holds only its implementations: `queue/redis/publisher.py`,
`queue/redis/consumer.py`. `config.py`, the base classes and `provider.py`
stay at the top, beside it.

What makes this pay:

- **The provider takes the whole config, not just the enum**, so it can hand each
  implementation the settings that belong to it and nothing else.
- **A selected option with no configuration is a hard error**, raised at bringup
  and naming the section that is missing. Never a silent default.
- **Consumers are typed against the base class only.** The controller holds a
  `BaseTableRepository`; it cannot name a concrete class, so it cannot grow a
  dependency on one.
- **Construction happens once, at the entry point**, and the collaborators are
  passed in. Nothing reaches for a provider part-way down a call stack.
- **Adding an option is purely additive**: a member, a config, a module, a
  registry entry. If adding one makes you edit an existing branch, the shape is
  wrong.

Worked examples: `lobby/repository/`, `game/repository/`.

## 6. Clean code

### Every function lives on a class

**No bare functions at module level.** A function is a `@staticmethod` on a class
named for the thing it does, so the call site carries that name with it:

```python
# no — the call site says nothing about where this came from
def position_key_for(state: ChessBoardState) -> PositionKey: ...

# yes
class PositionKeyBuilder:
    @staticmethod
    def build_key_from_state(state: ChessBoardState) -> PositionKey: ...
```

`PositionKeyBuilder.build_key_from_state(state)` reads as one phrase wherever it
appears. `position_key_for(state)` reads as a loose verb whose origin the reader
has to go and look up.

- **The class is the namespace.** Because it qualifies every call, the method name
  itself stays short: `PawnGeometry.start_rank(color)`, not
  `pawn_start_rank(color)` and not `PawnGeometry.pawn_start_rank_for_color(color)`.
- **Private helpers move onto the class too**, as `_`-prefixed static methods.
- **Constants stay at module level**, since they are named nouns rather than
  behaviour, but they must be explicit — see below.
- **The one exception is a process entry point.** A console script needs a
  module-level `main`. It parses the arguments, reads the configuration file
  they name, and hands it to one object — and it does nothing else. Bringup
  belongs to that object, in methods of its own; `main` stays short enough to
  read at a glance and never computes anything.

### Names must survive being imported

**Read every name as it will look in the file that imports it**, not in the file
that defines it. Inside `castling_geometry.py`, `WHITE_KINGSIDE` is obvious;
imported into a rules module it could be anything.

```python
from chess.models.castling_geometry import WHITE_KINGSIDE           # no
from chess.models.castling_geometry import WHITE_KINGSIDE_CASTLING  # yes
```

- **A lookup says what it maps.** `MATERIAL_VALUES_BY_PIECE_TYPE`, not
  `MATERIAL_VALUES`. `PIECE_TYPES_BY_PROMOTION_LETTER`, not `PROMOTION_LETTERS`,
  which names the keys while returning the values.
- **A method says what it returns or decides**, and the class supplies the
  subject: `AttackMap.is_square_attacked_by`, not `AttackMap.is_attacked_by`;
  `RayScanner.moves_along_rays`, not `RayScanner.moves`.
- **A lookup is `get_<thing>`.** `registry.get_client(game_type)`,
  `controller._get_participant(session, player_id)`,
  `registry.get_game_types()`. Never `client_for`, `participant_of`,
  `view_for`: a preposition says nothing about what comes back, and it reads
  differently at every call site.
- **A parameter names the thing, not its container.** `state: ChessBoardState`,
  not `board`, once the type says state.

### The rest

- **Names say what, not how.** `attacked_squares`, `is_in_check`,
  `relocated_to`. Booleans read as predicates: `is_terminal`, `is_empty`.
- **Functions do one thing** and stay at one level of abstraction. An entry point
  reads settings, delegates, and reports — it does not compute.
- **Fail fast, fail closed.** Validate at the boundary and raise with a message
  naming the actual values (`f"got {supplied!r}, expected one of {allowed}"`).
  Allowlists over denylists wherever data enters the system.
- **Comments explain *why*.** The code already says what. Comment the
  non-obvious constraint — why the scan stops after an enemy square, why the
  clock resets on a capture. Delete commentary that just restates the line.
- **Type-annotate signatures.** Public functions take and return named types.
- **No dead code.** Delete it; git remembers. An unused abstract base or a type
  nothing references is noise.

### Docstrings

**The opening quotes sit on their own line.** The text starts on the line below
them, always — including a docstring of a single sentence.

```python
"""
The position that results from playing this move.
"""
```

Never `"""The position that results...` on the same line as the quotes.

**Write for someone reading the file for the first time, every time.** A
docstring says what the thing is and what a caller must know to use it. It does
not narrate how the code came to be, argue against a design that was not chosen,
or lean on a decision explained somewhere else.

- Short, complete sentences. Two or three; rarely more.
- No conversational voice — no "the awkward one", "deliberately", "note that",
  "as decided", "this is why", "the worked example is".
- No comparison against code that is not there.
- Keep a constraint a caller could get wrong. Drop the commentary around it.

```python
# no — narrative, and only makes sense to someone who followed the argument
"""The awkward one: it moves and captures differently, and it changes into
something else. All three of its specials stay here rather than in the rules
layer, because each is decidable from the pawn's own square plus one fact the
board already publishes..."""

# yes
"""
A pawn. Moves forward, captures diagonally, promotes on the last rank.

Owns the double push, en passant and promotion. Each is decidable from the
pawn's own square and one board fact.
"""
```

A reason that a caller needs belongs in the docstring; a reason that only the
next editor needs belongs in a comment at the line it explains.

## 7. Explicit beats DRY — the local override

This repo prefers **replication over premature abstraction**, and that outranks
generic clean-code advice:

- No shared base classes to save a few lines. `Bishop`, `Rook` and `Queen` each
  subclass `BasePiece` directly and each names its own directions; there is no
  `SlidingPiece` tier in between.
- No shared private helpers to save a few lines — write each case out with a
  specific, descriptive name.
- Adapters/converters are static methods named `<source>_to_<target>`.

**The one thing that overrides *this*:** a subtle, correctness-critical algorithm
belongs in exactly one place. `RayScanner` is shared by bishop, rook and queen
because three hand-written copies of "walk until blocked, include an enemy square
then stop, exclude a friendly one" would be a bug farm. If you factor something
out for this reason, say why in the docstring.

## Checklist before finishing a file

- [ ] No `from __future__ import annotations`; every import at module top
- [ ] Touched `__init__.py` files still empty
- [ ] No bare literal carrying domain meaning — enum, constant, or config
- [ ] Every enum's base is its value type — `StrEnum`, `IntEnum`, or `Enum`
- [ ] Nothing crosses a layer as a `dict` or `tuple` that should be a dataclass
- [ ] Every parameter and return annotated; no bare `list`/`set`/`dict`, no `Any`
- [ ] No outside-system shape written as a bare literal — modelled in its own module with `to_dict`/`from_*`
- [ ] App settings come from a YAML file parsed into a dataclass — no `os.environ`, no `os.getenv`
- [ ] Any swappable collaborator is a `config.py` / `base_*.py` / concrete / `provider.py` package
- [ ] Consumers are typed against the base class, and built once at the entry point
- [ ] Every docstring opens with `"""` alone on its line, and reads to a first-time reader
- [ ] No bare module-level functions — each is a static method on a class that names it
- [ ] Every name still reads correctly in the file that imports it
- [ ] Dataclasses `frozen=True, slots=True` unless mutation is justified in the docstring
- [ ] Layering respected: no sideways or upward imports
- [ ] Pieces take `BoardStateView`, never `ChessBoardState`
- [ ] The engine package stays free of I/O — no `print`, no `input`
- [ ] Ran the suite, `ruff check` and `mypy`

## A review comment becomes a rule

When the author of this repository reviews any .py file and leaves a comment, decide
whether it is about the line or about the codebase.

- **About the line** — a wrong name, a missed case, a typo. Fix it and move on.
- **About the codebase** — a comment that would apply the same way to the next
  file, and the one after that. Fix the line, then write the rule into this
  skill, in the section it belongs to, in the same shape as the rules around it.

The test is whether the reviewer would have to say it again. If they would, the
skill is missing a rule, and leaving it unwritten means the next change makes the
same mistake and costs the same review.

Applying a comment to one file and not to the rule is the failure this section
exists to prevent. `backend-development`, `typescript-style` and `frontend-development` carry the same instruction for their own subjects.
