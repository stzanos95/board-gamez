---
name: modeling
description: How to model this system in protobuf. Load before writing or changing any .proto under idl/contracts/proto — a new message, a new enum, a new service, a new domain, or a change to an existing one. Covers the two hard rules of a modelling session (never generate, always explain), which of model/dto/obj/service a message belongs in, the layering that keeps a generic domain free of a specific one, and the system-design questions a schema has to answer before it is worth generating from.
---

# Modelling

Modelling is where this system's design gets decided. A schema is not a
transcription of what the code already does — it is the argument about what the
parts are, who owns them, and what they are allowed to know about each other.
Getting it wrong is expensive later, so it is worth many rounds now.

## The two hard rules

**Never generate.** Do not run `./idl/scripts/generate.sh`, and never write or
edit anything under `idl/contracts/gen`. Generation is the user's, always. Write
the `.proto` files, say what changed, and stop. `lint.sh`, `format.sh` and
`breaking.sh` are fine — they produce no generated code — but say what you ran.

The reason is not ceremony. Generated output is a large diff that hides the small
one that matters, and a modelling session should end with the user reading six
lines of schema, not six hundred lines of descriptor.

**Always explain the abstraction.** Every message, every enum, every field that
is not obvious comes with the reasoning. Not what it is — the schema says that —
but why it is shaped that way. A change handed over without its reasoning cannot
be argued with, and arguing with it is the point.

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
- **`dto/`** — does the caller need a shape the domain does not have? A
  projection that hides something, an aggregate assembled for one screen, a
  request body. When the API's shape and the domain's shape are the same, send
  the model and leave `dto/` empty. An empty `dto/` is a finding, not a gap.
- **`obj/`** — does the store need a shape the domain does not have? An index, a
  partition key, a denormalised copy, a row that two versions of the code must
  both read. A model that doubles as a row cannot change without a migration.
- **`service/`** — what can be called, and on what path. Requests and responses
  live in `dto/`, not here.

If a message seems to belong in two, it is probably two messages that happen to
have the same fields today. Say so and let the user decide.

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
- **Explicit presence where absence means something.** `optional` on a scalar or
  enum that is genuinely sometimes absent. Message fields already have presence;
  do not decorate them.
- **A record is a message, a collection is `repeated`.** If reading a field
  correctly depends on remembering an order or a spelling, it wants a message.
  `repeated Move` is a collection; a `repeated string` whose first element is an
  id is a record that has not been named.
- **Name a field for what it is in the file that reads it**, not the file that
  declares it. `seat_to_act`, not `current`.
- **Comment the why.** The field name says what. The comment says what a reader
  would get wrong: that `captured_square` differs from `destination` for en
  passant, that `position_keys` runs one ahead of `turns`.

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
- [ ] Each message is in the right one of `model` / `dto` / `obj` / `service`
- [ ] No generic domain imports a specific one
- [ ] Every enum starts at `_UNSPECIFIED`, and no number was reused
- [ ] `option go_package` on every new file
- [ ] Concurrency, visibility, recovery and participant count are answered or named as open
- [ ] Open questions are listed, not silently decided
