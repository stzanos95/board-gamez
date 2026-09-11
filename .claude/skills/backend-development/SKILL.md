---
name: backend-development
description: The layer a component belongs to, and what it may depend on. Load before adding or changing any backend component — a router, a servicer, a client, a controller, a repository, an adapter, or a deployable. Covers the five layers and where each lives in this repository, the api → service → controller → repository chain with adapters between, what each layer is forbidden to do, how dependencies are constructed and passed, and how SOLID decides the boundaries rather than only the classes.
---

# Backend development

`ARCHITECTURE.md` at the repository root defines the layers and maps every path
to one. This skill is the working rule set: what you may write in the layer you
are standing in, and what belongs one layer down.

## The chain

```
api  →  service  →  adapter  →  controller  →  repository  →  store
```

- **api** — a deployable. Reads configuration, constructs collaborators, serves.
- **service** — the binding between a transport and a controller. A router, a
  servicer, or an outbound client.
- **adapter** — conversion between the types of two adjacent layers.
- **controller** — the rules. The only layer that decides anything.
- **repository** — storage and retrieval, behind an interface.
- **store** — the database.

Each arrow crosses a boundary. A component may call the layer below it and the
adapters beside it. It may not call two layers down, and it may not call upwards.

## What each layer may do

### api — `deployables/<app>/`

Reads one YAML file into a frozen dataclass, constructs every collaborator, and
starts a server. It contains no route, no message and no rule.

- Construction happens here and nowhere else. A controller, a repository and a
  client are built at bringup and passed down.
- Nothing reads the environment. A container passes a path to a config file, not
  the settings themselves.
- Adding a domain is a dependency and one line.

### service — `packages/<domain>/…/service/`

One file per transport binding. It adapts, calls the controller, and adapts what
comes back.

- **No field is read off a request here.** `request.table_id` in a service is a
  conversion, and conversions belong to an adapter.
- No conditional that changes an outcome. A branch above the controller is logic
  in the wrong layer.
- Transport concerns are legitimate: status codes, headers, casing the framework
  dispatches on, connection lifecycle.
- The generated base class or servicer is what a service implements. It never
  redeclares the operations the schema already declares.

### adapter — `packages/<domain>/…/adapters/`

Static methods, one per direction, named `<source>_to_<target>`.

- Every conversion is a named method, including a one-field access. The service
  reads uniformly, and a change to a request shape touches one file.
- An adapter that would return two values wants either two methods or a named
  type. It never returns a tuple standing in for a record.
- An adapter decides nothing and calls nothing but a converter.

### controller — `packages/<domain>/…/controller/`

The rules. Every validation, every refusal, every ordering decision.

- **Takes the arguments an operation needs, never a request.** `read_table(
  table_id: str)`, not `read_table(ReadTableRequest)`. A dto reaching the
  business layer couples the rules to a transport and stops a second transport
  from reusing them.
- Speaks the domain's own types: `model`, never `dto`, never `obj`.
- **What it answers with is a type from the schema's `model/`.** An outcome
  and the view that goes with it is `idl.game.model.CommandResult`, and the
  response carries it. A dataclass declared beside the controller to carry an
  answer is a model that has not been written down, and a second definition
  of something the schema already says.
- Holds its collaborators, received in `__init__`. It does not construct them and
  does not reach for a provider part-way down a call.
- Is typed against a repository's base class, never a concrete store.

### repository — `packages/<domain>/…/repository/`

Storage and retrieval. It answers what is stored and where, never what it means.

- A swappable collaborator, so it is four files: `config.py`, `base_*.py`, one
  concrete implementation per file, and `provider.py` holding a registry and a
  static factory.
- Reads and writes the types in the schema's `obj/`, and converts to `model` at
  its own boundary.
- Contains no rule. "Refuse a write built on an old version" is enforced here as
  a compare-and-set, but the decision that it must be refused is the controller's.

## No domain error handling yet

**No package declares an exception of its own.** There is no `errors.py`, no
domain base class, and nothing above a layer catches what it raised. An
error-handling library is coming, and it will decide how a refusal travels; until
it lands, code written against a hand-rolled hierarchy has to be unpicked.

Until then, a component reports an outcome through the type it already answers
with:

- A read that found nothing answers `None`.
- A write that was refused answers `None`, and the response leaves the field
  unset. The schema already has a way to say a table is not there.
- An operation with nothing to report answers `None` and reports nothing.

Two things still raise, and neither is a domain error:

- **Bad configuration**, at bringup, with a builtin — a selected option whose
  settings section is missing stops the process before it serves.
- **A library**, on its own terms. Nothing catches it yet.

## Dependency direction

```
deployable  →  package  →  contracts
```

One direction, with no exceptions.

- A package never imports a deployable.
- A domain package never imports another domain package. Domains reference each
  other by identifier, and a name is joined when a view is assembled.
- `packages/core` is imported by anything and imports no domain.
- A generic layer never imports a specific one. The session layer carries a
  game's state as `google.protobuf.Any` and never unpacks it.

### A game is two packages, and the line between them is the platform contract

```
packages/<game>            the rules. Imports idl.<game>.model and nothing else
                           from the schema. Knows nothing about participants,
                           sessions or the platform.
packages/product-<game>    the product. The only package that imports both
                           `game` and `<game>`. Implements BaseRules and
                           RulesService, converts between the platform's types
                           and the game's, decides what a participant number
                           means in the game, and serves the game's own
                           service over the platform's session.
```

There is no product process. `grpc-server` depends on the product, builds its
rules at bringup, registers its servicers beside the platform's, and hands the
session controller the rules in-process through `RulesRegistry`. A product
reached over a network later is another implementation of `BaseRules`.

What goes where, by the question it answers:

- "Is this move legal, what is the position now, who won on the board" —
  `packages/<game>`. It computes over `idl.<game>.model` types and declares no
  type the schema already names; it may be reimplemented in another language
  against the same schema.
- "Which participant is white, what is `participant_to_act` after this ply, how
  does a `GameResult` read for participant 2, how is a `GameState` payload
  unpacked" — `packages/product-<game>`. Anything that names a participant, a
  session, a `GameState` or an `Action` is the product's, never the rules'.
- "Which seats a player may take, and what each one is in this game" —
  `packages/product-<game>`, as a `BaseSeating` implementation. It answers a
  list of `SeatChoice`s, each a seat number and a role packed as `Any`, and
  writes nothing. The lobby's `SeatController` owns the rules every game
  shares — a seat is taken only while the table waits, a player holds one seat,
  a choice must be one the game offered — and does the write.
- "Who may start the game, how the platform's answer reads to a player of this
  game" — `packages/product-<game>`, in the controller behind the game's own
  service. It composes the platform's controllers (`TableController`,
  `SeatController`, `SessionController`) in-process. The game's own service is
  also where a seat is taken with the role opened: a browser playing chess
  sends a `Color`, and the product packs it.
- A role is packed and opened in exactly one adapter in the product. No file in
  `lobby`, `game` or the browser reads one.
- `packages/game` imports no product. Adding a game is a `GameType` member, a
  product package, a dependency of both deployables, and one entry each in the
  rules registry and the seating registry in `grpc-server`.

## SOLID decides the boundaries

The principles apply to the layers, not only to the classes inside them.

- **Single responsibility** — a layer has one reason to change. A transport
  change affects the service. A rule change affects the controller. A storage
  change affects the repository. If one change touches two layers, the boundary
  is in the wrong place.
- **Open/closed** — a new game is an enum member and an implementation. A new
  domain is a package and one line at bringup. If adding something requires
  editing an existing branch, the shape is wrong.
- **Liskov** — every implementation of a contract answers with the same meaning,
  and the caller does not check which one it holds.
- **Interface segregation** — a layer receives what it uses. A controller
  receives a `table_id`. A piece receives a `BoardStateView`, not the board.
- **Dependency inversion** — depend on the contract. The concrete store is
  selected at bringup from configuration.

## Adding a component

1. Name the layer it belongs to, using the table in `ARCHITECTURE.md`.
2. Write it in that layer's directory, under that layer's constraints.
3. If it needs a value from the layer above, add an adapter method. Do not read
   the field where you stand.
4. If it needs a collaborator, take it in `__init__` and construct it at the
   entry point.
5. If the change spans two layers, stop and find the misplaced piece.

## Checklist

- [ ] The component is in the directory its layer owns
- [ ] No service or adapter contains a conditional that changes an outcome
- [ ] No field is read off a request outside an adapter
- [ ] The controller takes arguments, not a request, and speaks `model` only
- [ ] Collaborators arrive in `__init__` and are constructed at the entry point
- [ ] The controller names no concrete store
- [ ] No package declares an exception; an outcome travels as the answer's own type
- [ ] No package imports a deployable, and no domain imports another domain
- [ ] Nothing reads the environment; settings come from the YAML file
- [ ] The change touches one layer

## A review comment becomes a rule

When the author of this repository reviews a router, a servicer, a controller, a repository, or an adapter and leaves a comment, decide
whether it is about the line or about the codebase.

- **About the line** — a wrong name, a missed case, a typo. Fix it and move on.
- **About the codebase** — a comment that would apply the same way to the next
  file, and the one after that. Fix the line, then write the rule into this
  skill, in the section it belongs to, in the same shape as the rules around it.

The test is whether the reviewer would have to say it again. If they would, the
skill is missing a rule, and leaving it unwritten means the next change makes the
same mistake and costs the same review.

Applying a comment to one file and not to the rule is the failure this section
exists to prevent. `python-style`, `typescript-style` and `frontend-development` carry the same instruction for their own subjects.
