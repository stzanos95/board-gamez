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
| `packages/core/` | Shared utilities | No domain-specific code. `core/queue` is the broker every domain publishes to and consumes from, behind a provider |
| `packages/game/` | Application, Business, Persistence | A game being played, whatever game it is. Imported by every domain package; imports none of them, and never a product |
| `packages/chess/` | Business (one game's rules) | Chess rules only. Every chess type is `idl.chess.model`'s; the package adds behaviour. Knows nothing about tables or participants |
| `packages/product-chess/` | Application and Business (one product) | Chess as the platform hosts it. The only package importing both `game` and `chess` |
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
 └─ POST /internal/platform/lobby/join/table
    fastapi-gateway                     Application: HTTP transport
     └─ LobbyRouters → HttpSeatService  Application: binding
        └─ SeatAdapters                 adapter: pydantic to protobuf
           └─ GrpcSeatClient            Application: outbound transport
              ─────────── network ───────────
              grpc-server                Application: gRPC transport
               └─ LobbyServicers → GrpcSeatService   Application: binding
                  └─ SeatAdapters       adapter: dto to model
                     └─ SeatController  Business: the decision
                        └─ TableController → TableRepository   Persistence
                        │                     └─ Redis      Database
                        └─ BaseQueuePublisher   the event, after the write
```

Each step downwards removes knowledge. The gateway handles HTTP and has no
concept of a table. The servicer handles gRPC and has no concept of what
joining means. The controller defines what joining means and has no concept of
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
`HttpTableService`. Both expose the same three operations. A queue consumer would
be a third and would require no change below the Application layer.

### The browser renders, and does not decide

The presentation layer draws what it is given and sends what a person asked
for. A rule it evaluated would be a second copy of that rule, on a machine this
project does not control, that drifts from the first.

Nothing over the wire writes a table. `TableService` reads and retires;
opening a table and joining one are `SeatService.CreateTable` and `JoinTable`,
decided by the lobby's `SeatController` and recorded as events. A seat is taken
through the game's own service as one of the `SeatChoice`s the game offered;
a seat is given up through the lobby's `SeatService`, which withdraws the
player from the game being played before it opens the seat. What a withdrawal
does to the game is answered by the game's rules through
`RulesService.WithdrawParticipant`: in chess the leaver resigns.

### The platform does not interpret games

A table names a `GameType` and seats N players. A game's rules, position and
legal moves reach the session layer as `google.protobuf.Any`, which is stored and
relayed without being unpacked. What a seat is in the game's own terms — the
side it plays, the token it moves — is a `role` on the seat, carried the same
way: packed by the product when the seat is taken, handed to the rules when the
game starts, and never opened by `lobby` or `game`. Which seats a player may
take, and with which role, is answered by the product's `BaseSeating`, found
by game type in the lobby's `SeatingRegistry`. Adding a game requires a
`GameType` member, a product package, and one entry each in the rules registry
and the seating registry at bringup. No file in `lobby` or `game` changes.

A game is two packages. `packages/chess` is the rules and performs no I/O: no
printing, no reading, no storage, so it is callable from a CLI, a server, or a
test. `packages/product-chess` implements the platform's `RulesService` over
those rules, decides what a participant number means in chess, and serves
`ChessService`: the same game with its state opened, so a browser plays chess
through chess's own types. `grpc-server` holds the product's rules in-process
and hands them to the session controller; there is no product process.

### Domains reference each other by identifier

`lobby` stores a `player_id`, not a `Player`. A stored copy of another domain's
model becomes stale when that domain changes it, and it places one domain's shape
inside another's storage. Display names are joined when a view is assembled.

`game` is the exception in one direction: it is the platform every domain is
built on, so any domain package may import it and call its controllers. A
table hosts a game, and the lobby withdraws a player from that game when they
give up their seat. `game` imports no domain package in return.

### Configuration is a file, and construction happens once

Each app is brought up from a YAML file parsed into a frozen dataclass. No
component reads the environment. Collaborators — controller, repository, client —
are constructed at the entry point and passed down. No component obtains a
dependency part-way through a call.

### One writer per invariant

A table is written in one place, guarded by the version it was read at.

### Every write is an event, and a browser is told only that something changed

Each controller write that succeeds publishes one event — `SeatTaken`,
`CommandApplied`, `ParticipantWithdrawn` — declared in the domain's
`model/event.proto`, carrying the version after the write. Events travel in
`QueueMessageEnvelope` through `core.queue`, whose publisher and consumer are
selected by configuration; the controller holds a `BaseQueuePublisher` and
names no broker.

An event is the backend's record and holds full information, including an
action only its sender may see. A browser is never sent one. It is sent
`TableChanged` or `SessionChanged` — an id and a version — and reads the view
it renders through the typed service it already uses, which projects it for
that viewer. Projection therefore happens in one place, on the read path.

A channel is a string, and each domain names its own: the lobby publishes on
`table:<id>` and `lobby`, the platform on `session:<id>`. `core.queue` carries
the name and never reads it.

`deployables/websocket-server` is the process between the two. It holds a
`BaseQueueConsumer` per configured source and the open sockets by the channel
each watches, subscribes a channel while a socket watches it, and turns each
event into the `*Changed` frame for the watchers of the channel it arrived on.
It holds no gRPC client and reads nothing from an event but an id and a
version.

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
