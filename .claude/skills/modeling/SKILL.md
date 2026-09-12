---
name: modeling
description: How to model this system in protobuf. Load before writing or changing any .proto under idl/contracts/proto — a new message, a new enum, a new service, a new domain, or a change to an existing one. Covers the two hard rules of a modelling session (never generate, always explain), which of model/dto/obj/service a message belongs in, the layering that keeps a generic domain free of a specific one, and the system-design questions a schema has to answer before it is worth generating from.
---

# Modelling

These rules address whoever writes the code, a developer or an assistant. A
step a rule leaves to "the user" — running the generator, committing — is the
developer's own when they work alone.

Modelling is where this system's design gets decided. A schema is not a
transcription of what the code already does — it is the argument about what the
parts are, who owns them, and what they are allowed to know about each other.
Getting it wrong is expensive later, so it is worth many rounds now.

## The two hard rules

**Never generate.** An assistant does not run `./idl/scripts/generate.sh`,
and never writes or edits anything under `idl/contracts/gen`. Generation is the
developer's, always: an assistant writes the `.proto` files, says what changed,
and stops. A developer working alone writes the schema, reads it back, and then
runs the generator themselves. `lint.sh`, `format.sh` and `breaking.sh` are
fine for either — they produce no generated code — but say what you ran.

The reason is not ceremony. Generated output is a large diff that hides the small
one that matters, and a modelling session should end with the user reading six
lines of schema, not six hundred lines of descriptor.

**Always explain the abstraction — in the reply, never in the schema.** Every
message, every enum, every field that is not obvious comes with the reasoning.
Not what it is — the schema says that — but why it is shaped that way. A change
handed over without its reasoning cannot be argued with, and arguing with it is
the point.

That reasoning goes in the reply to the person who asked, and nowhere else. **It
never goes in a comment**, and there is nowhere else for it to go: see below.
A comment is read years later by someone who did not follow the argument, cannot
see the alternative it rejects, and does not care which directory the type lives
in. The rules in `CLAUDE.md` hold — no conversation context, no comparison
against code that is not there, and never the name of an implementation the
contract does not bind to.

**No README lives under `contracts/proto`.** Not per domain, not per directory.
A schema documents itself through names, and prose beside it goes stale the first
time a field changes and nobody remembers the file exists. A rule that outlives
one conversation belongs in this skill, where it is loaded before the next
change. Everything else belongs in the reply and is allowed to be forgotten.

An explanation is worth reading when it says:

- **What forced the boundary.** Why this is one message and not two, or two and
  not one. Why this field is on the table and not on the move.
- **Which layer owns it, and why the dependency points down.**
- **What was deliberately left out**, and what would have to change for it to
  come back.
- **What alternative shape was rejected**, and what it would have cost. "A oneof
  over game types would read better in TypeScript but would make `table` import
  `chess`" is a sentence the user can disagree with. "Used Any" is not.
- **Which system-design question it settles**, and which it leaves open.

State open questions rather than deciding them quietly. A modelling session that
surfaces a disagreement early has done its job; one that buries a decision in a
field name has not.

## Where a message goes

Each domain under `idl/contracts/proto/idl/<domain>/` splits four ways, and the
split is what keeps one change from becoming three.

```
model/     what a thing is
dto/       what an API hands out and takes in
obj/       what a repository reads and writes
service/   what can be called
```

The test for each:

- **`model/`** — would this still exist if there were no API and no database?
  Domain vocabulary, one message per dataclass and one enum per enum. It says
  nothing about how it is stored or asked for.
- **`dto/`** — transfer, and only transfer. `<Method>Request` and
  `<Method>Response`, nothing else. A view, a summary or a projection is not a
  dto: anything that survives being read is a model, and a response carries the
  model. If a caller seems to need a different shape, ask whether it needs a
  different model or whether it can derive what it wants — a client knows its own
  identity, so nothing has to be answered per viewer.
- **`service/`** — what can be called, and where. The requests and responses it
  names live in `dto/`.
- **`obj/`** — **is this a row?** A type here earns its place by being something
  the store writes and reads as a unit. If a `Seat` is only ever held inside a
  table's row, there is no `SeatObj`; the row uses the model's `Seat`. If seats
  are written and read on their own, there is. Nothing else goes here: an index,
  a partition key or a denormalised copy is a row too, and gets its own type.

If a message seems to belong in two, it is probably two messages that happen to
have the same fields today. Say so and let the user decide.

## Stored types restate their fields

**A row declares its own fields. It never embeds the model as a field.**
Composing a wrapper around a model looks tidier and is wrong: it welds storage to
the domain, so every model change is a migration, and it forbids the store from
ever holding less than the whole thing.

```
package idl.lobby.obj;

message TableObj {                       // yes
  idl.core.obj.ObjectMetadata metadata = 1;
  idl.lobby.model.GameType game_type = 2;
  repeated idl.lobby.model.Seat seats = 3;
  ...
}

message TableObj {                       // no — the model, wrapped
  idl.core.obj.ObjectMetadata metadata = 1;
  idl.lobby.model.Table table = 2;
}
```

**A row's own fields are restated; what nests inside them is not.** The row is
what evolves on the store's schedule, so its shape is the store's. A value held
inside it — a seat in a table's row — is the model's type, because a parallel
copy with no independent reason to exist is two things to keep in step for
nothing.

What restating buys: storage can carry a field the domain has no idea about, omit
one it does not need, keep a denormalised copy for an index, and change shape on
its own schedule. What it costs is a mapping to maintain and two definitions to
keep honest. That is the trade, made deliberately, and it is the repository's
"explicit beats DRY" rule applied to persistence.

**Share the enums, duplicate the messages.** A field number is local to the
message that declares it, so a duplicated message shape can never collide with
the original. An enum value is written into the data, so a second declaration
that drifts in numbering silently reinterprets every row already stored. Import
the model's enums; restate the model's messages.

**`ObjectMetadata` is the one thing every stored type shares** — identity, the
version optimistic concurrency turns on, and the audit fields. Being written down
is what makes concurrent writers possible, so the version belongs to the metadata
rather than to each thing stored.

## Domains, and what `core` is for

**`core` holds only what every domain needs and no domain owns** — transport
envelopes, object metadata. It is not the place for concepts that were hard to
file. Tables, seats and players are domain vocabulary and belong to a domain of
their own; putting them in `core` is how a shared layer becomes a layer that
everything depends on and nobody can change.

**A domain is named for what it is about, not for what it contains.**
`identity` owns who someone is, and later how they prove it. `lobby` owns where
people gather to play. `chess` owns one game's rules.

**Domains reference each other by id, never by embedding.** A seat holds a player
id; it does not hold a `Player`. A copy of another domain's model is a copy that
goes stale the moment that domain changes it, and it drags one domain's shape
into another's storage. The name to draw beside a seat is joined in when a view
is assembled, which is one of the things `dto/` is for.

## Endpoint paths

Every path is built the same way:

```
/<internal or external>/<platform or product>/<domain>/<method>/<entity>

/internal/platform/lobby/read/table
/internal/platform/lobby/join/table
```

- **internal or external** — who may call it. `internal` is reached from inside
  the system; `external` faces a browser or a third party. Nothing is `external`
  yet.
- **platform or product** — which half owns it. `platform` is what every game
  shares; a product is one thing built on top. `chess` is a product:
  `/internal/product/chess/start/game`.
- **domain** — the directory the service lives in.
- **method** — `upsert`, `read`, `delete`, `list` for storage. A domain verb
  (`join`, `leave`) belongs to a layer above storage, never beside it.
- **entity** — singular, and a row. Not a field of one.

**An internal method exists for a row, and for nothing smaller.** The entities a
service acts on are exactly the types in `obj/`. If a seat is not a row, there is
no `UpsertSeat`: changing one is a read of the table, an edit, and a write of the
table back, guarded by the version. A method that edits part of a row is a domain
verb wearing a storage name, and it drags the store's write pattern into a
contract that should not know it.

The cost is that two callers editing different parts of one row conflict on the
version and one retries. That is the correct outcome — neither write is lost —
and where the contention is high enough to hurt, the answer is that the part
should have been its own row all along.

**The entity stays singular in the method name too.** `ListTable`, never
`ListTables` — the method names what it acts on, and the plural belongs to what
comes back. So the storage methods are `ReadTable`, `DeleteTable` and
`ListTable`, and their messages follow.

**A write never crosses a boundary as a storage method.** Every write that
succeeds is an event, and an event is published by the controller that decided
the write. An `UpsertTable` over the wire is a write nothing decided and
nothing announced, so a store service exposes reads and retirements, and every
write arrives as a domain verb (`CreateTable`, `JoinTable`, `TakeSeat`) on a
service above it. The controller keeps `upsert` as the operation those verbs
end in.

**A listing returns a collection model, never a repeated field.**

```
message TableCollection {                      // idl.lobby.model
  repeated Table table_items = 1;
}

message ListTableResponse {                    // idl.lobby.dto
  idl.lobby.model.TableCollection collection = 1;
}
```

`<Entity>Collection` holds `repeated <Entity> <entity>_items`, and the response
carries it as `collection`. Whatever a listing grows next — a count, a cursor,
the filter it was answered under — lands in one place and every listing gets it,
instead of being added to a response at a time.

The method is in the path, so **every call is a POST with the request as its
body**, a read included. A GET cannot carry one.

## Naming

**A name never repeats its container.** The directory, the package and the
message are already part of every call site, so saying it again is noise that
compounds.

```
lobby/obj/table.proto        idl.lobby.obj.Table       // yes
lobby/obj/table_object.proto idl.lobby.obj.TableObject // no — obj, twice
message Player { string id; }                          // player.id
message Player { string player_id; }                   // no — player, twice
```

**Rows are the one exception: a type in `obj/` ends in `Obj`.**
`idl.lobby.obj.TableObj`, not `idl.lobby.obj.Table`. A row and its model are
routinely in scope together — a writer maps between them — and two types called
`Table` in one function is exactly where a mapping goes wrong silently. The
suffix is worth the repetition where the reader is holding both at once.

**`id` when the message is the thing. `<thing>_id` when it points at one.**

```
message Player { string id = 1; }                     // player.id
message Seat   { optional string player_id = 3; }     // seat.player_id
message GetTableRequest { string table_id = 1; }      // names a table, is not one
```

`player.player_id` says the same word twice at every call site. `seat.id` says
nothing about which id it is.

## Layering

**A generic domain never imports a specific one.** `table` is about N players
taking turns; `chess` is about bishops. `table` importing `chess` would mean
adding a game changes the session layer, which is the thing the split exists to
prevent. The dependency runs one way, and there is no exception worth taking.

**Opacity is a design tool.** When a layer must carry something it has no
business understanding, carry it as `google.protobuf.Any`. The session layer
stores and relays a game's state without opening it; only the game service and
the client that plays that game unpack it. This costs a type registry on the
TypeScript side and buys a server that hosts games it has never heard of.

Reach for `Any` when the alternative is an upward import or a `oneof` that every
new implementation has to edit. Do not reach for it to avoid naming a type that
the layer genuinely does own.

## Transfer layers are envelopes

**A boundary that moves messages gets an envelope: a header and a payload.**
Never a bare message on the wire, and never a transport that has to open a
payload to know what to do with it.

**But an envelope supplies what a transport lacks — check that first.** A socket
frame is bytes with no identity, type or routing, so it needs one. A queue
message is the same, portably. HTTP and gRPC are not: both already carry
headers, an id convention and a status, and wrapping them puts a second envelope
inside the first. That gives two places carrying a request id and two places
saying whether it worked, which is how you get clients checking the wrong one.
It also flattens every endpoint in the generated OpenAPI into one opaque
`{header, payload}`, spending that whole target on symmetry.

Symmetry is the trap. Three transports modelled alike looks tidier than two, and
that is not a reason. The exception is a transport whose body genuinely lacks a
type — a webhook receiver, or one endpoint multiplexing many message kinds —
where the envelope is supplying something missing rather than duplicating
something present.

- **The header is what the transport reads.** Identity, what the message means,
  when it was emitted, and whatever routing and delivery need. If a transport has
  to unpack the payload to route, log or acknowledge, the header is missing a
  field.
- **The payload is `google.protobuf.Any`.** Packed by the domain that produced
  it, opened only by the domain that consumes it. This is what lets one relay
  carry messages whose types it was never compiled against.

**Not all transfer headers are the same, so do not share one.** Model a header
per transport, even when the fields are identical on the day you write them. A
socket frame has a connection behind it and often a client waiting on an answer;
a queue message outlives its sender, is delivered more than once, and may be
replayed long after. Those facts imply different fields, and they arrive at
different times. One shared header means every field either applies everywhere or
is documented as ignored somewhere — and a field that is meaningless on one
transport is worse than a second message. This is the repository's "explicit
beats DRY" rule at its most load-bearing.

**No envelope carries a status.** An outcome — accepted, rejected, and why — is a
payload type named by `type`, so a consumer branches the same way on every
transport. The header addresses; the payload means. A status in both places is
two sources of truth for the same question.

**`type` on a header is the one string this repository tolerates for a closed
set.** The transport layer cannot enumerate the message types of domains it must
not import; that is the same constraint that makes the payload opaque. The
obligation moves outward rather than away: each domain owns the constants for its
own types, and an unknown type is a runtime decision.

Before an envelope is finished, ask what its transport actually needs that a bare
send does not: correlating an answer to its question, carrying a trace across a
hop, noticing a redelivery, keeping an order, telling when something happened
apart from when it arrived. Add the ones its transport has, and say which ones
you left out.

## What a schema has to answer

Most of the system design is decided here, whether or not anyone notices. Before
a domain is worth generating from, walk these and say what the answer is — or
that it is open.

- **Who writes this, and is there exactly one writer?** Two producers of one
  invariant is a bug the schema can prevent.
- **Does the writer exist yet?** A field whose only writer is a layer that has
  not been built is not modelled, however obvious it seems. Cache a fact another
  layer owns only when the round trip it saves has a measured cost, and never
  before that layer exists — until then it is a second copy of a truth with
  nobody to keep it honest.
- **Can this field contradict another one?** Two fields that must agree are one
  field and a derivation. If a status enum has exactly the values that a
  nullable id already distinguishes, one of them is redundant.
- **What happens when two writers race?** If the answer is a version field,
  model it now — retrofitting optimistic concurrency means every client changes.
- **Who is allowed to see this?** Perfect information is an assumption, not a
  default. A game with a hidden hand needs a per-viewer projection, and adding
  one later is a breaking redesign.
- **How does a reader that missed a message recover?** Fan-out that does not
  promise delivery needs a sequence a client can notice a gap in, and a way to
  ask for what it missed.
- **Where does this live, and does it survive a restart?** State that only exists
  in a process is a different message from state that is written down.
- **How many participants?** Two is a special case of N. A field called `white`
  and a field called `black` is a decision that chess is the only game.
- **What does a client do with each way this fails?** A closed enum of reasons
  beats a string, because a client can branch on it: a version conflict is worth
  a silent retry, an illegal action is worth telling the player.
- **What breaks when this changes?** Additive changes are free; renames,
  renumbers and moves are not. If a field looks likely to move, ask whether it is
  in the right message now.

## Shape

- **Closed sets are enums**, starting at `_UNSPECIFIED = 0`. proto3 requires a
  zero value, and it is what a reader sees when a newer schema has not set the
  field. No producer ever writes it.
- **Never `optional`.** Absence is the zero value: `UNSPECIFIED` on an enum, the
  empty string, zero on a number. Message fields already carry presence and need
  no decoration.
- **Where zero is a real value, number from one.** This is the one trap the rule
  above sets. Seat 0 is a legitimate seat, so `seat_to_act = 0` would be
  ambiguous between "seat zero acts" and "nobody acts" — so seats are numbered
  from 1 and 0 means none. `File` and `Rank` already do this. Where renumbering
  is wrong, carry a companion boolean (`is_you`, `is_seated`) instead of
  overloading a sentinel nobody will remember.
- **A record is a message, a collection is `repeated`.** If reading a field
  correctly depends on remembering an order or a spelling, it wants a message.
  `repeated Move` is a collection; a `repeated string` whose first element is an
  id is a record that has not been named.
- **Name a field for what it is in the file that reads it**, not the file that
  declares it. `seat_to_act`, not `current`.
- **Comment what a reader would get wrong**, not why you chose it. That
  `captured_square` differs from `destination` for en passant, that
  `position_keys` runs one ahead of `turns`, that a timestamp is emission and not
  receipt. A comment that only makes sense to someone who followed the design
  discussion belongs in the reply instead.
- **A message may carry a long comment. A field may not.** Everything a reader
  needs — what the type is, the constraint they would otherwise get wrong, what a
  caller is obliged to do — goes in the block above the message. A field comment
  is **one short sentence, trailing the field on the same line**, and never a
  block above it.

  ```
  message Seat {
    uint32 number = 1;
    SeatStatus status = 2;
    string player_id = 3;  // Empty exactly when the seat is OPEN.
  }
  ```

  A field that seems to need two sentences needs one of them above the message,
  where it is read once instead of skimmed past every time. A field whose name
  already says it needs no comment at all.
- **A contract never names what is behind it.** No store, no framework, no
  transport it is not itself defining. A model does not know who holds it. If a
  type is a cache, that belongs in its name — `CachedTable` — not in a comment.

## Mechanics that will bite

- **`option go_package` on every file.** Go is not a target; the OpenAPI
  generator is a Go program and refuses a file without one.
- **Never renumber a field, and never reuse a number.** Deleting one means
  `reserved`. `breaking.sh` enforces it against `main`.
- **buf lint is `STANDARD` minus `PACKAGE_VERSION_SUFFIX`.** So: package matches
  directory, enum values prefixed with the enum name, services suffixed
  `Service`, and every RPC's messages named `<Rpc>Request` and `<Rpc>Response`
  and used by exactly one RPC.
- **The `idl/` path segment is load-bearing.** It is the Python import root, and
  protoc derives that from the file path. Do not flatten it.

## How an iteration goes

1. Say what question this round is answering, in a sentence.
2. Write or change the `.proto` files, and nothing else.
3. Explain each abstraction against the list above — why this shape, what was
   rejected, what it costs.
4. Name what is still open, and what would settle it.
5. Hand back. The user generates.

Expect to be wrong about something every round. That is the process working: it
is much cheaper to lose an argument about a field name than to migrate one.

## Checklist before handing back

- [ ] Nothing under `idl/contracts/gen` was written, and the generator was not run
- [ ] Every non-obvious message and field has its reasoning stated in the reply
- [ ] Field comments are one sentence, trailing the field; long prose sits above
      the message
- [ ] No comment carries conversation context, a rejected alternative, or the
      name of a store, framework or implementation
- [ ] Each message is in the right one of `model` / `dto` / `obj` / `service`
- [ ] `dto/` holds only `<Method>Request` and `<Method>Response`
- [ ] Method names take a singular entity, and listings return a collection model
- [ ] No README was added under `contracts/proto`
- [ ] Every endpoint path follows internal/platform/domain/method/entity
- [ ] Every internal method acts on a row, never on part of one
- [ ] Each message is in the right domain, and `core` gained nothing a domain owns
- [ ] Every type in `obj/` is a row, restates the row's own fields, and ends in `Obj`
- [ ] Cross-domain references are ids, not embedded models
- [ ] Identifiers are `id` on the owner and `<thing>_id` on a reference
- [ ] No name repeats its directory, package or message
- [ ] No generic domain imports a specific one
- [ ] Every enum starts at `_UNSPECIFIED`, and no number was reused
- [ ] No `optional` anywhere; anything numbered where 0 is real starts at 1
- [ ] `option go_package` on every new file
- [ ] Concurrency, visibility, recovery and participant count are answered or named as open
- [ ] Open questions are listed, not silently decided
