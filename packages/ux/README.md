# ux

The presentation layer: what the browser renders, and the hooks behind it.

Every line of frontend TypeScript lives here. `deployables/gamez-ux` is the
shell that mounts it — bringup, settings, the bundler and the container — and
holds no domain code, so adding a screen never touches it.

```
src_tsx/
├── theme/        the design system
├── transport/    how a request reaches the gateway, and how an answer is cached
├── identity/     who is playing
├── routing/      which screen is on
├── format/       turning a value into text
├── lobby/        one domain: its gateway calls, its hooks, its labels
├── components/   rendering only
└── runtime/      the collaborators, built once
```

Rules for working here are in `.claude/skills/frontend-development/` and
`.claude/skills/typescript-style/`. Read both before changing anything.

## The boundary

**This layer renders. It does not decide.**

A component never calls the gateway, never holds a query, and never knows a URL.
It receives values and callbacks. A hook is what binds a screen to a domain, and
a domain module is what talks to the gateway.

## Talking to the gateway

Every message on the wire is built from `@board-gamez/idl`. No request shape and
no field name is written here.

```ts
const response = await client.unary(TableService.method.readTable, { tableId });
```

`GatewayClient` reads the path off the method's own `google.api.http` option, so
the URL an operation is served at is stated once, in the `.proto` that declares
the operation. Bodies and answers are proto3 canonical JSON, produced and read
by the schema.

## The one decision made here

`lobby/table_intents.ts` produces new tables, and `lobby/seat_writer.ts` writes
them. `TableService` is a store with four methods and no verb for taking a seat,
and nothing between it and a browser decides, so taking a seat is a read, a
change, and a write guarded by the version that was read.

This is business logic in the presentation layer. It is confined to those two
files: a `JoinSeat` operation on the lobby turns each function into one call,
and no component changes.

## Two screens, and which one you are on

The screen is not a free choice. A player who is seated at a table is shown that
table; a player who is seated nowhere browses the list. Each screen sends the
viewer to the other when the data says they are on the wrong one, so a reload
lands you back at your table and giving up a seat returns you to the list.

The list is a table of tables: index, name, game, seats taken over seats, and
status. Its only action is joining, because a table you are not seated at is not
a screen you can be on. Opening a table seats the player who opened it.

A table's name is derived from its identifier. `idl.lobby.model.Table` has no
name field; adding one is a schema change.

## Freshness

The lobby list and a table are polled, at intervals the deployable's settings
name. Polling stops while the tab is hidden, so a background tab issues no
requests and holds no timer. Real-time game state is not this: it arrives over
the WebSocket server.

## Identity

`identity/player_session.ts` holds a player id in session storage, which is
per-tab. **A second browser tab is a second player**, which is what lets a table
be filled from one browser. It is the shape an authenticated session will have,
and it is the file sign-in replaces.
