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
├── chess/        one game: its gateway calls, its hooks, its views, its labels
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

## No decision is made here

The browser never writes a table. Opening one and joining one are the lobby's
`CreateTable` and `JoinTable`; a seat is taken through the game's own service
as one of the choices it offered; a seat is given up through the lobby's
`SeatService`. Every one of those is decided by a controller behind the
gateway, and the browser sends what was asked and draws what came back.

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

## Playing a game

A table shows its game's screen above the seats. Five records keyed by
`GameType` bind a game into the shell, and none compiles until every game has
an entry: `components/table/GameScreen.tsx` picks the screen,
`components/common/GameArtwork.tsx` the picture, `lobby/table_labels.ts` the
name and whether a table of it can be opened,
`runtime/game_change_keys_registry.ts` the queries a change to the table
reaches, and `runtime/packed_types.ts` the types the game packs into a payload.
Chess is `chess/` and `components/chess/`.

The screen holds three things: which square is picked up, whether a promotion
is being chosen, and whether a resignation is being confirmed. What a piece may
do is the `legalMoves` list the game sends; clicking a square that is the
destination of one of them sends that move, and nothing in the browser computes
a move. Whose turn it is comes from `state.sideToMove` and the session's
`color`; a spectator has no colour and sees the board with no controls.

The board is composed from parts a skin supplies. `components/chess/skins/` is
a seam in the same shape as `theme/`: `board_skin_name.ts` selects,
`board_skin.ts` is the contract, one file per skin, and `board_skin_registry.ts`
maps the enum to them. A skin is a palette, a shape for each `PieceType`, the
ground of a square, and the frame around the squares. `ChessBoard` draws
sixty-four `ChessSquare`s, each holding a `ChessPiece`, and reads every colour
and shape from the skin in reach. The configured skin is the default; the
player's own pick is kept in local storage.

## Freshness

A change reaches the browser as a `TableChanged` or `SessionChanged` frame on
the socket, carrying an id and a version. `lobby/use_table_changes.ts` and
`lobby/use_lobby_changes.ts` compare the version with what the cache holds and
read the affected queries again through the gateway. Nothing is written into
the cache from a frame; it carries nothing to write.

While the socket is down, the lobby list, a table and a game are polled at the
intervals the deployable's settings name under `freshness`. Polling stops while
the tab is hidden, and a game is polled only while someone else can change it.

## Identity

`identity/player_session.ts` holds a player id in session storage, which is
per-tab. **A second browser tab is a second player**, which is what lets a table
be filled from one browser. It is the shape an authenticated session will have,
and it is the file sign-in replaces.
