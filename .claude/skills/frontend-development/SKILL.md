---
name: frontend-development
description: The presentation layer — what it may do, what it must push to the backend, and what a browser is allowed to cost. Load before adding or changing anything under packages/ux or deployables/gamez-ux — a component, a hook, a query, a theme, a transport client, or the deployable's bringup. Covers the boundary between rendering and deciding, the three seams (theme, transport, identity), talking to the gateway through the generated stubs, TanStack Query as the only cache, the rules that keep a weak machine responsive, and when to stop and ask for a backend change.
---

# Frontend development

`ARCHITECTURE.md` names five layers. This is layer 1, presentation, and it is the
only layer that runs on a machine this project does not control.

`typescript-style` governs how the code is written. This governs what it is
allowed to do.

## The boundary

**The frontend renders. It does not decide.**

A decision is anything a second client would have to reimplement to behave the
same way: what a legal move is, whether a table may start, who may sit where,
what a score is, what happens when two people act at once. Every one of those
belongs to a controller. A browser that decides them holds a second copy of the
rules that drifts from the first, and it holds them where a user can edit them.

What the frontend legitimately owns:

- **Rendering** — turning a value into an element.
- **Derivation for display** — a label, a count, a sort, a filter over data
  already in hand. Cheap, reversible, and wrong only on screen.
- **Intent** — collecting what the user wants and sending it.
- **Presentation state** — which dialog is open, which row is expanded, what is
  typed into a field that has not been submitted.

When a decision has nowhere to live below this layer, that is a gap in the
backend. **Say so, and ask before filling it here.** If it is filled here as a
stopgap, it goes in exactly one file, named for what it decides, so that moving
it later is one file and one call site.

Today there is one such stopgap: `packages/ux/src_tsx/lobby/table_intents.ts`.
`TableService` is a store with four methods and no domain verbs, so taking a seat
is a read, a change, and a write guarded by the version that was read. That file
is the only place in the frontend that produces a new `Table`.

## Where things live

```
packages/ux/src_tsx/      every line of frontend TypeScript
deployables/gamez-ux/     the shell: bringup, config, Vite, the container
```

The deployable holds no domain code. It reads a config file, mounts the app, and
serves the build. Adding a screen never touches it.

Inside `packages/ux/src_tsx`, a directory is a concern, not a layer:

```
theme/        the design system, and nothing that knows about a table
transport/    how a request reaches the gateway, and how a response is cached
identity/     who is playing
routing/      which screen is on
lobby/        one domain: its gateway calls, its intents, its hooks, its labels
components/   rendering only
```

A domain directory holds hooks and pure functions. `components/` holds elements.
**A component never calls the gateway and never holds a query.** It receives
values and callbacks. A hook is what binds a screen to a domain.

## The three seams

Each is a swappable collaborator in the shape `typescript-style` rule 5 defines:
an enum, a contract, one file per option, and a record that selects.

### theme

Every colour, spacing, radius and font in the application comes from the theme.
**No component writes a colour.** `sx={{ color: "text.secondary" }}` reads the
theme; `sx={{ color: "#8a8a8a" }}` is a bug that a redesign has to hunt for.

A theme is a token file. Changing how the whole product looks is changing which
token file the config names, and nothing else.

### transport

One client reaches the gateway, and it is the only thing in the frontend that
knows a URL exists. Everything above it calls a typed function.

### identity

Who is playing is read from one module. Today that is a per-tab id in
`sessionStorage`, so a second tab is a second player and the lobby can be tested
with one browser. **It is deliberately the shape an authenticated session will
have**, so replacing it is one file.

## Talking to the gateway

**Every message on the wire is built from `@board-gamez/idl`.** No hand-written
request interface, no hand-written response interface, no string field name.

```ts
const request = create(ReadTableRequestSchema, { tableId });
const body = toJson(ReadTableRequestSchema, request);
const response = fromJson(ReadTableResponseSchema, json, { ignoreUnknownFields: true });
```

- **`toJson` and `fromJson` are the wire format.** They produce and read proto3
  canonical JSON — camelCase names, enums as their declared names, 64-bit
  integers as strings — which is the same encoding the gateway's pydantic models
  use. Neither side writes the mapping down.
- **`ignoreUnknownFields` is set on every read.** A gateway that has been
  redeployed with a newer schema sends a field a running browser does not know,
  and a browser that has been open for a day must not break on it.
- **A path is read from the service descriptor**, not typed into a client. The
  `google.api.http` option is in the generated descriptor, so the URL a method is
  served at comes from the contract that declares it.
- **`bigint` stays `bigint`.** `version` is `uint64`. It is carried and sent
  back, never converted to `number`, and never rendered without being made a
  string deliberately.

## TanStack Query owns the cache

**There is one cache, and it is the query cache.** Server data is never copied
into `useState`, never mirrored into a context, and never held in a module
variable.

- **A key is built by one function per query**, so no two call sites can spell a
  key differently. Keys are hierarchical, so invalidating a domain invalidates
  its members.
- **A mutation ends by invalidating what it changed**, and nothing else. Refetch
  the table that was written, not every table.
- **`staleTime` is set deliberately on every query.** It is what stops a
  remount from being a request. Zero is a choice that has to be justified.
- **A write is not optimistic unless it cannot fail.** A table write is guarded
  by a version and can be refused, so the screen shows what the server answered.
- **A refused write is retried by re-reading, once.** A refusal means the value
  moved; it does not mean the request was malformed, and it is not an error to
  show the user until the retry has also been refused.

## What a browser is allowed to cost

Assume the machine is slow and its memory is small.

- **No `setInterval` that is not a query's own `refetchInterval`.** One timer per
  mounted screen, at most.
- **Polling stops when the tab is hidden.** `refetchIntervalInBackground` is
  false, always. A background tab must cost nothing.
- **An interval is read from configuration**, so tuning it is not a code change.
- **A list row is a memoised component.** It takes the values it draws, not the
  object it belongs to, so a change to one row does not re-render the others.
- **Nothing is computed in a render that could be computed once.** A derivation
  over server data belongs in a `useMemo` keyed on that data, or in a pure
  function called by the hook that owns the query.
- **Nothing loops over data the backend could have counted.** If a screen wants a
  number the server already knows, ask for the number.
- **No dependency is added to look at data.** Sorting, filtering and grouping are
  a few lines. A library for them is megabytes on a connection that may be slow.

### When to push work down

Stop and ask before writing any of these in a browser:

- A loop over a collection that grows without a bound the server enforces.
- Anything that would be wrong if two clients did it at once.
- Any derivation a second client would have to copy to agree.
- Anything read on a timer that a socket could push instead.

Real-time game state is already decided: it arrives over the WebSocket server,
not by polling. `idl/core/dto/websocket.proto` is the envelope it travels in.
Lobby operations go over the gateway.

## Configuration is a file

The app is brought up from `deployables/gamez-ux/config/gamez_ux.json`, fetched
before React mounts and parsed into one frozen object. **Nothing reads
`import.meta.env`, and nothing reads a variable baked in at build time.**

This is the rule every other deployable here follows, and it buys the same
thing: one image runs against any gateway, with any theme, at any polling
interval, by mounting a different file. A value baked into a bundle is a rebuild.

A config that is missing, malformed, or naming a theme that does not exist stops
bringup with a message. It never falls back to a default.

## Adding a screen

1. Add the gateway call to the domain's gateway module, built from the
   generated schemas.
2. Add a hook that owns the query or the mutation, its key, and its freshness.
3. Add components that take values and callbacks and render them.
4. Add the route.
5. Nothing in `deployables/gamez-ux` changes.

## Checklist

- [ ] No component calls the gateway, holds a query, or knows a URL
- [ ] No decision was made in the browser that a second client would have to copy
- [ ] Every request and response is built from a generated schema
- [ ] `ignoreUnknownFields` is set on every read, and `version` stays a `bigint`
- [ ] Server data lives only in the query cache
- [ ] Every query sets `staleTime`, and every mutation invalidates what it wrote
- [ ] No timer except a query's `refetchInterval`, and none of them run hidden
- [ ] Every colour, space and radius comes from the theme
- [ ] Every list row is a memoised component taking values, not objects
- [ ] Settings come from the config file — no `import.meta.env` anywhere

## A review comment becomes a rule

When the author of this repository reviews a component, a hook, a query, or the deployable's bringup and leaves a comment, decide
whether it is about the line or about the codebase.

- **About the line** — a wrong name, a missed case, a typo. Fix it and move on.
- **About the codebase** — a comment that would apply the same way to the next
  file, and the one after that. Fix the line, then write the rule into this
  skill, in the section it belongs to, in the same shape as the rules around it.

The test is whether the reviewer would have to say it again. If they would, the
skill is missing a rule, and leaving it unwritten means the next change makes the
same mistake and costs the same review.

Applying a comment to one file and not to the rule is the failure this section
exists to prevent. `typescript-style`, `backend-development` and `python-style` carry the same instruction for their own subjects.
