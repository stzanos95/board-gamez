# Architecture

A multiplayer board-game platform. People sit at tables, take seats, and play a
game that the platform hosts without interpreting its rules.

This document defines the layers, states which layer a given file belongs to, and
lists what each layer may depend on. The table in "Which layer am I in?" answers
the common case by file path.

## The five layers

| # | Layer | Responsibility | Location here |
| - | ----- | -------------- | ------------- |
| 1 | **Presentation** | User interface | `packages/ux/`, served by `deployables/gamez-ux/` |
| 2 | **Application** | Transport, routing, coordination. No rules | `deployables/*`, and `<domain>/service/` |
| 3 | **Business** | Rules and decisions | `<domain>/controller/` |
| 4 | **Persistence** | Storage and retrieval | `<domain>/repository/` |
| 5 | **Database and hosting** | State and execution environment | Redis, `infra/`, each deployable's `docker/` |

Adapters sit between layers, in `<domain>/adapters/`. They are not a layer. They
convert values so that neither adjacent layer needs to know the other's types.

## Which layer am I in?

| Path | Layer | May contain decisions |
| ---- | ----- | --------------------- |
| `deployables/gamez-ux/` | Presentation (hosting) | No. Reads configuration, mounts the app, serves the bundle |
| `packages/ux/…/components/` | Presentation | No. Receives values and callbacks, and draws them |
| `packages/ux/…/<domain>/` | Presentation (binding) | No. Calls the gateway and shapes answers for a screen |
| `deployables/<app>/` | Application (transport) and hosting | No. Reads configuration, builds collaborators, serves |
| `packages/<domain>/…/service/` | Application (binding) | No. Adapts, calls, adapts |
| `packages/<domain>/…/adapters/` | Between layers | No. One named method per conversion |
| `packages/<domain>/…/controller/` | Business | Yes. This is the only layer that decides |
| `packages/<domain>/…/repository/` | Persistence | Only about storage, never about meaning |
| `packages/core/` | Shared utilities | No domain-specific code |
| `packages/chess/` | Business (one game's rules) | Chess rules only. Knows nothing about tables |
| `idl/contracts/proto/…/model/` | Business vocabulary | Definitions of what a thing is |
| `idl/contracts/proto/…/dto/` | Application transfer | Definitions of what crosses a boundary |
| `idl/contracts/proto/…/obj/` | Persistence shapes | One type per stored row |
| `idl/contracts/proto/…/service/` | Application surface | Callable operations and their paths |
| `infra/` | Hosting | Compose files and scripts |

A change that requires editing two layers indicates that something is in the
wrong layer.

## One call through the stack

A player joins a table. The path:

```
gamez-ux                                Presentation: a browser
 └─ TableGateway → GatewayClient        Presentation: outbound transport
    ─────────── network ───────────
    nginx, forwarding /api              Presentation: hosting
 └─ POST /internal/platform/lobby/upsert/table
    fastapi-gateway                     Application: HTTP transport
     └─ LobbyRouters → HttpTableService  Application: binding
        └─ TableAdapters                 adapter: pydantic to protobuf
           └─ GrpcTableClient            Application: outbound transport
              ─────────── network ───────────
              grpc-server                Application: gRPC transport
               └─ LobbyServicers → GrpcTableService   Application: binding
                  └─ TableAdapters       adapter: dto to model
                     └─ TableController  Business: the decision
                        └─ TableRepository   Persistence
                           └─ Redis      Database
```

Each step downwards removes knowledge. The gateway handles HTTP and has no
concept of a table. The servicer handles gRPC and has no concept of what an
upsert means. The controller defines what an upsert means and has no concept of
where a table is stored.

## Decisions

### Contracts are generated, and nothing crosses a boundary untyped

Every message between layers or processes is generated from
`idl/contracts/proto`: protobuf for gRPC, pydantic for HTTP, TypeScript for a
browser, OpenAPI for documentation. Two sides of a boundary never declare
separate definitions of the same type.

The schema's four-way split corresponds to the layers:

```
model/     what a thing is                  Business vocabulary
dto/       what crosses a boundary          Application transfer
obj/       what a store holds               Persistence
service/   what can be called, and where    Application surface
```

### Only the controller decides

A servicer adapts, calls, and adapts back. A router does the same. A client
converts and sends. None of them reads a field from a request in order to branch
on it. A conditional above the controller indicates logic in the wrong layer.

The controller takes the arguments an operation requires — `read_table(table_id)`
rather than `read_table(ReadTableRequest)`. A dto therefore never reaches the
business layer, and a second transport can call the same controller.

### Two transports, one controller

`TableService` is served over gRPC by `GrpcTableService` and called over HTTP by
`HttpTableService`. Both expose the same four operations. A queue consumer would
be a third and would require no change below the Application layer.

### The browser renders, and does not decide

The presentation layer draws what it is given and sends what a person asked
for. A rule it evaluated would be a second copy of that rule, on a machine this
project does not control, that drifts from the first.

`TableService` is a store with four methods and no domain verb, and nothing
between it and a browser decides yet, so taking a seat is currently a read, a
change and a version-guarded write made in
`packages/ux/src_tsx/lobby/table_intents.ts`. That is business logic above the
Application layer. It is in one file so that a `JoinSeat` operation on the lobby
replaces it with a call.

### The platform does not interpret games

A table names a `GameType` and seats N players. A game's rules, position and
legal moves reach the session layer as `google.protobuf.Any`, which is stored and
relayed without being unpacked. Adding a game requires a `GameType` member and
one service implementation. No file in `lobby` changes.

`packages/chess` performs no I/O: no printing, no reading, no storage. It is
therefore callable from a CLI, a server, or a test.

### Domains reference each other by identifier

`lobby` stores a `player_id`, not a `Player`. A stored copy of another domain's
model becomes stale when that domain changes it, and it places one domain's shape
inside another's storage. Display names are joined when a view is assembled.

### Configuration is a file, and construction happens once

Each app is brought up from a YAML file parsed into a frozen dataclass. No
component reads the environment. Collaborators — controller, repository, client —
are constructed at the entry point and passed down. No component obtains a
dependency part-way through a call.

### One writer per invariant

A table is written in one place, guarded by the version it was read at.

## SOLID applied to system design

These principles are usually stated about classes. They also determine the
boundaries between layers.

- **Single responsibility** — a layer has one reason to change. A transport
  change affects the gateway. A rule change affects the controller. A storage
  change affects the repository. One change affecting two layers indicates a
  misplaced boundary.
- **Open/closed** — extend by adding. A new game is a `GameType` member and an
  implementation. A new domain is a package and one line at bringup. Editing an
  existing branch to add something indicates a design problem.
- **Liskov** — implementations of a contract are substitutable. Every game
  service answers `CreateGame`, `ApplyAction` and `ListLegalActions` with the same
  meaning, and the session layer does not check which game it holds.
- **Interface segregation** — each layer receives only what it uses. A controller
  receives a `table_id`, not a request. A chess piece receives a
  `BoardStateView`, not the board.
- **Dependency inversion** — depend on the contract, not the implementation. A
  controller holds a repository interface; the concrete store is selected at
  bringup from configuration. Dependencies run `deployable → package → contracts`
  in one direction.

## The repository layer

A swappable collaborator, with the structure used elsewhere in this repository:

```
repository/
├── config.py                  the selecting enum and one config per option
├── base_table_repository.py   the operations any store must answer
├── redis_table_repository.py  one implementation per file
├── redis_table_row.py         the keys and fields that implementation writes
└── provider.py                a registry and a static factory
```

The controller is typed against the base class, so it cannot reference a concrete
store. The provider is called once, at the entry point.

A repository reads and writes the schema's `obj/` types, and the conversion to
`model` runs in the domain's adapters. A table is stored as a hash carrying its
version alongside the encoded table, and every write compares that version inside
Redis, so a write built on a version that has since moved on changes nothing.

## Reading order

1. This document.
2. `idl/README.md` — the contracts and how they are generated.
3. `.claude/skills/backend-development/SKILL.md` — rules for working in a layer.
4. `.claude/skills/python-style/SKILL.md` — rules for writing the code.
5. `.claude/skills/modeling/SKILL.md` — rules for changing the schema.
