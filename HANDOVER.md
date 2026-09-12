# Handover

Transient. Delete it once the work below has landed.

Where the platform got to, what is decided, and what the next agent builds: the
chess screen in the browser. Written for an agent picking this up cold.

## Read these first, in this order

1. `ARCHITECTURE.md` — the five layers, and which one a path belongs to.
2. `CLAUDE.md` — how to write. The comment rules are strict and enforced in review.
3. The skills, each loaded **before** the work it governs:
   - `.claude/skills/frontend-development/` — before anything under `packages/ux`.
     Read "The boundary" and "TanStack Query owns the cache" twice.
   - `.claude/skills/typescript-style/` — before any `.ts` or `.tsx`. Rules 1, 2
     and 3 are the ones review catches most.
   - `.claude/skills/modeling/` — only if a `.proto` has to change. Nothing
     below needs one.

**Never run the generator.** `./idl/scripts/generate.sh` is the author's. The
chess schema is generated and committed; everything this work needs is in
`idl/contracts/gen/typescript/src/idl/chess/`.

**A review comment becomes a rule.** When the author leaves a comment that would
apply to the next file too, fix the line and write the rule into the skill.

## State: what runs today

```bash
./infra/scripts/build.sh          # every image; name one to build one
./infra/scripts/up.sh             # the stack in containers, detached
./infra/scripts/down.sh
```

Open **http://localhost:8081**. Every browser tab is a different player: a
player id is minted per tab into `sessionStorage`
(`packages/ux/src_tsx/identity/player_session.ts`). `up.sh` rebuilds images
whose source changed and recreates their containers. After a frontend change:
`./infra/scripts/up.sh`, then a hard reload.

Without containers, with Redis on 6379 (the compose `redis` service is enough):

```bash
./deployables/grpc-server/scripts/local-serve.sh        # 50051
./deployables/fastapi-gateway/scripts/local-serve.sh    # 8080
./deployables/gamez-ux/scripts/local-dev.sh             # 5173, proxies /api to 8080
./deployables/gamez-ux/scripts/local-typecheck.sh       # tsc --noEmit, in a container
```

The frontend has no test suite. `tsc --noEmit` and driving the screen are the
checks.

Every backend project is green: chess 150 (+1 skipped perft), lobby 19, game 35, product-chess 28, grpc-server 5, gateway 7;
`pre-commit run --all-files` passes.

## What exists

### The backend loop, end to end

A chess game is started, read and played through **`ChessService`**, served by
the gateway at:

```
POST /internal/product/chess/start/game     StartGameRequest  { tableId, playerId }
POST /internal/product/chess/read/game      ReadGameRequest   { tableId, playerId }
POST /internal/product/chess/play/action    PlayActionRequest { tableId, playerId, commandId, action, expectedVersion }
```

Every request carries `playerId` as a field: identity is the caller's claim
until an identity layer exists. `version` and `expectedVersion` are `uint64`,
so `bigint` in TypeScript and strings on the wire.

What comes back is **`ChessSession`** (`idl/chess/model/session.proto`):

```
id                the table's id
game              ChessGame: roster, state, history, legal_moves, status, resigning_color, result
color             the side the viewer plays; UNSPECIFIED for a spectator
last_command_id   the command that produced this game
version           counts writes; send it back as expectedVersion
```

and, from `PlayAction`, **`ActionResult { CommandOutcome outcome; ChessSession
session }`**. `session` is set for every outcome except `SESSION_NOT_FOUND`.

`CommandOutcome` (`idl/game/model/command_result.proto`) is what the screen
branches on:

| Outcome | What it means for the screen |
| ------- | ---------------------------- |
| `APPLIED` | The action is in the game; render `session`. |
| `ALREADY_APPLIED` | A retry of a command that already landed; render `session`, say nothing. |
| `VERSION_MOVED` | The game moved since it was read; render `session` (it is current) and let the player choose again. Not an error. |
| `OUT_OF_TURN` | Not this player's turn. Render `session`. |
| `ILLEGAL_ACTION` | The rules refused it. Cannot happen if the move came from `legal_moves`. |
| `NOT_A_PARTICIPANT` | A spectator tried to play. |
| `GAME_OVER` | The game has a result. |
| `SESSION_NOT_FOUND` | No game at this table. `session` unset. |

**`StartGame`** answers `session` unset when the table is not chess, has an open
seat, or the caller is not seated; a table already playing answers the game
already there. Each seat plays the side it was taken with: `ListSeatChoice`
offers the open seats with their sides (seat 1 White, seat 2 Black), and
`TakeSeat` takes one of those choices.

**What the game carries that the screen needs**, all in `session.game`:

- `state.occupancy`: the pieces, as `SquareOccupant { square, occupant }`. Only
  occupied squares are listed, in no promised order.
- `state.sideToMove`, `state.enPassantTarget`, `state.castlingRights`, the
  clocks.
- `legalMoves`: every `Move` the side to move may play, empty once the game is
  over. **This is the only source of what a player may do.** A move is chosen
  from it; nothing in the browser computes legality.
- `history.turns`: `ChessTurn { number, player, move, notation, resultingStatus }`
  — `notation` is standard algebraic ("Nf3", "O-O", "e8=Q#"), ready to print.
- `status`, `resigningColor`, `result { outcome, winner, status, resigningPlayer }`.
- `roster.white.participant`, `roster.black.participant`.

**What a player sends** is `ChessAction`, a oneof: `{ kind: { case: "move",
value: CoordinateMove } }` or `{ kind: { case: "resignation", value: {} } }`.
`CoordinateMove { origin, destination, promotionType }` — `promotionType` is
set only when a pawn reaches the last rank, and a promotion is matched only when
it says what the pawn becomes.

The generated TypeScript enums drop the prefix: `File.A`, `Rank.RANK_1`,
`Color.WHITE`, `PieceType.PAWN`, `GameStatus.CHECKMATE`, `MoveType.CASTLE`,
`CommandOutcome.APPLIED`.

Verified with curl and, in the last round, driven end to end: start → e2e4
`APPLIED` → same command `ALREADY_APPLIED` → White again `OUT_OF_TURN` → stale
version `VERSION_MOVED` → e7e5 `APPLIED` → e4e5 `ILLEGAL_ACTION` → onlooker
`NOT_A_PARTICIPANT` → resignation `APPLIED` with a result → anything after
`GAME_OVER` → spectator read with no colour.

### The frontend, as it is

`packages/ux/src_tsx/`, React 19, MUI 7, TanStack Query 5, `@bufbuild/protobuf`
2. Two screens: the lobby (`components/lobby/`) and a table
(`components/table/TableScreen.tsx`). Routing is the fragment:
`#/` and `#/table/<id>` (`routing/route.ts`).

The pattern every screen follows, and the chess screen copies:

```
lobby/table_gateway.ts       one class over the generated service; answers the model, never the response
lobby/table_queries.ts       one function per query key
lobby/use_table.ts           the query hook: key, fetch, refetchInterval from config, staleTime from the client
lobby/table_views.ts         pure derivations for display: labels, counts, isMine
lobby/use_table_actions.ts   mutations; each ends by adopting or invalidating what it wrote
components/table/            elements only; values and callbacks in, nothing fetched
```

- **Transport**: `transport/gateway_client.ts`. `client.unary(Service.method.x,
  request)` builds the request with `create`, sends `toJson`, reads `fromJson`
  with `ignoreUnknownFields`. The path is read from the method descriptor.
  Nothing else knows a URL.
- **Services**: `runtime/app_services.tsx` holds `tableGateway` and `freshness`;
  `runtime/AppRoot.tsx` builds them once from the config. A hook reaches for a
  gateway through `useTableGateway()`; a component never does.
- **Identity**: `usePlayer()` → `{ player: { id, displayName }, rename }`.
- **Config**: `deployables/gamez-ux/config/gamez_ux.json`, parsed by
  `config/ux_config.ts` with no defaults. `freshness.tableIntervalMs` is the
  table screen's `refetchInterval`; the query client sets
  `refetchIntervalInBackground: false` and `staleTime` for every query.
- **Theme**: `theme/theme_tokens.ts` is the contract, `midnight_tokens.ts` and
  `daylight_tokens.ts` the options. `palette.seat` is the worked example of a
  domain palette reaching `sx` as `"seat.mine"`. No component writes a colour.
- **The one stopgap**: `lobby/table_intents.ts` produces a new `Table` for join,
  sit, stand and leave, because `TableService` has no domain verbs. It is the
  only file that decides anything, and it stays that way.

## Decided

- **A product is two packages and no process.** `packages/chess` is the rules,
  `packages/product-chess` the product, `grpc-server` holds both in-process.
  Every chess type is the schema's; the engine adds behaviour. Read the
  `packages/chess/` row in `ARCHITECTURE.md` and rule 3 of `python-style`.
- **The browser talks to `ChessService`, never to `SessionService`, for chess.**
  The façade exists so that no `Any` is packed or opened in a browser. The
  protobuf-es type registry the earlier handover listed is not needed for this
  screen.
- **The browser renders. It does not decide.** Legal moves come from
  `legalMoves`. Whose turn it is comes from `state.sideToMove` and `color`.
  Whether the game is over comes from `result`. The screen's only choices are
  which square is selected and which dialog is open.
- **Polling is the bridge to fan-out.** Real-time state will arrive over a
  WebSocket through Redis pub/sub; neither exists yet. Until they do, the chess
  session query refetches on `freshness.gameIntervalMs`, the same way the table
  screen polls today, and stops when the tab is hidden. That is one option on
  one query, and it comes out the day the socket goes in.

## Next: the chess screen

### 1. Configuration

`deployables/gamez-ux/config/gamez_ux.json` gains `freshness.gameIntervalMs`
(2000 is fine locally). `config/ux_config.ts` reads it with
`readPositiveInteger`, no default. `FreshnessSettings` gains the field.

### 2. `packages/ux/src_tsx/chess/` — the binding

- `chess_gateway.ts`: `ChessGateway` over `ChessService` from
  `@board-gamez/idl/chess/service/game_pb`, three methods answering
  `ChessSession | null` for `start` and `read`, and `ActionResult` for `play`.
  Constructed in `AppRoot.tsx` beside `TableGateway`; `AppServices` gains
  `chessGateway` and `app_services.tsx` a `useChessGateway()`.
- `chess_queries.ts`: `chessQueryKeys.all`, `.session(tableId)`.
- `use_chess_session.ts`: the query. `queryFn` calls `gateway.read(tableId,
  player.id)`; `refetchInterval: freshness.gameIntervalMs` while a game is in
  progress and it is not this viewer's turn (a function of the data is allowed
  as `refetchInterval`; return `false` to stop). A `null` answer is "no game
  yet", not an error. Returns one named object: `{ board, moves, status,
  isLoading, hasGame, error }` built from `chess_views.ts`.
- `use_start_game.ts`: the mutation. On success with a session, `setQueryData`
  on the session key and invalidate the table detail (the table screen decides
  whether to show the board from whether a game exists).
- `use_play_action.ts`: the mutation. Mints `commandId` with
  `crypto.randomUUID()` **once per intent, at the moment the player commits**,
  and keeps it for a retry of that intent; carries the `version` of the
  session that was showing as `expectedVersion`. On any outcome that carries
  a session, `setQueryData` on the session key with it — every outcome's
  session is current. Map `CommandOutcome` to what the player is told through
  a `Record<CommandOutcome, string | null>` in `chess_labels.ts`; `APPLIED`,
  `ALREADY_APPLIED` and `VERSION_MOVED` say nothing.
- `chess_views.ts`: pure derivations, all `useMemo`'d by the hook:
  - `BoardView`: sixty-four `SquareView { file, rank, key, isLight, occupant
    (color, pieceType) | null, isSelected, isLegalTarget, isLastMoveSquare }`
    in draw order for the viewer (rank 8 first for White and a spectator,
    rank 1 first for Black). The occupancy list is indexed once by
    `file * 8 + rank` style key, never scanned per square.
  - `legalTargetsByOrigin`: `ReadonlyMap<squareKey, readonly Move[]>` from
    `legalMoves`, built once per session version.
  - `TurnView[]` for the move list: number, white notation, black notation,
    from `history.turns` paired by `number`.
  - `GameStatusView`: whose move it is, in check or not, the result sentence
    (`GameOutcome` and `GameStatus` through records in `chess_labels.ts`), and
    `canAct` = viewer's colour equals `state.sideToMove` and no result.
- `chess_labels.ts`: `Record`s keyed by the generated enums: piece glyphs by
  `PieceType` and `Color` (Unicode figurines, as the CLI draws them), file
  letters by `File`, rank digits by `Rank`, outcome sentences by `GameOutcome`,
  status sentences by `GameStatus`, outcome messages by `CommandOutcome`.

### 3. `packages/ux/src_tsx/components/chess/` — the elements

- `ChessScreen.tsx`: takes `tableId`, calls the three hooks, binds every
  section to a `const`, lays them out. Selection state (`useState` of a square
  key or null) lives here; it is presentation state. Clicking a square with
  the viewer's own piece selects it; clicking a legal target sends
  `CoordinateMove { origin, destination }`; clicking anything else clears.
  When the chosen target has more than one legal move (a promotion), a
  `PromotionDialog` asks which piece and the move's `promotionType` is set from
  the answer. A "Resign" button sends the resignation, behind a confirm.
- `ChessBoard.tsx`: a CSS grid of 64 `ChessSquare`s. `ChessSquare` is a
  memoised component taking the values it draws and one stable
  `onSelect(squareKey)`; it makes its own handler with `useCallback` (rule 2).
- `MoveList.tsx` with a memoised `TurnRow`.
- `GameStatusBanner.tsx`: whose move, check, result.
- `PromotionDialog.tsx`.
- Board colours are theme tokens: add `board: { light, dark, selected, target,
  lastMove }` to `ThemeTokens`, both token files and `build_mui_theme.ts`
  (`palette.board`), the way `seat` is done. No component writes a colour.

### 4. Where the screen lives

The table screen shows the board once a game exists. `TableScreen.tsx` gains:

- a "Start game" button, shown when `summary.isFull` and the viewer
  `isSeated`, calling `useStartGame`;
- the `ChessScreen` below the heading when `useChessSession(tableId).hasGame`,
  with the seat list collapsed to the roster.

No new route is required. If a route is wanted for a direct link, it is
`#/table/<id>/game` in `routing/route.ts`, and nothing else changes.

### 5. Verify

`./deployables/gamez-ux/scripts/local-typecheck.sh` clean. Then, with Redis,
grpc-server, the gateway and `local-dev.sh` up, in two tabs: create a chess
table, sit in both, start, play Scholar's mate from both tabs, watch the other
tab update within `gameIntervalMs`, resign a second game, open a third tab as
a spectator and confirm it sees the board with no controls. Then the container
path: `./infra/scripts/up.sh`.

Two verification techniques without a browser, if needed: bundle a throwaway
`.mts` with esbuild (`node_modules/.bin/esbuild`, with the banner
`import{createRequire as __cr}from'module';const require=__cr(import.meta.url);`)
and `renderToString` the screens; or drive `GatewayClient` and `ChessGateway`
against a running gateway. Delete the throwaway file.

## Gotchas that will cost you an hour

- **Proto3 JSON omits zero values.** A spectator's `color` is absent from the
  JSON, and `fromJson` gives `Color.UNSPECIFIED`; `participantToAct: 0` is
  absent too. Read the parsed message, never the raw JSON.
- **A oneof in protobuf-es is `{ case, value }`.** `create(ChessActionSchema,
  { kind: { case: "move", value: coordinateMove } })`. Sending `{ move }` sets
  nothing.
- **`version` stays a `bigint`.** Compare with `===` against another `bigint`;
  render with `String(version)` on purpose.
- **A message field that is unset is `undefined`** in protobuf-es
  (`session.game?.result`), not an empty message as it is in Python.
- **`legalMoves` is empty once the game is over**, and `state.sideToMove` still
  names a side. `result` is what says the game is over.
- **The npm workspace is rooted at the repository**; installing inside a member
  duplicates React. Run npm through `deployables/gamez-ux/scripts/npm.sh`.
- **`up.sh` rebuilds what changed.** A frontend change is `up.sh` then a hard
  reload; the dev server on 5173 needs no rebuild.
- **The table screen already polls** on `tableIntervalMs`. Two queries on one
  screen is two timers; keep the session query's interval the only one that
  runs while a game is in progress if a slow machine shows it.

## Open questions

- **Identity.** `playerId` is the caller's claim; the turn guard is only as
  strong as it. The author's.
- **Fan-out.** Redis pub/sub from the session controller to a WebSocket in the
  gateway, the nginx `Upgrade` headers, `ws: true` in Vite. The envelope is
  `idl/core/dto/websocket.proto`. Replaces the polling interval above.
- **The table's status never flips to `IN_PROGRESS`.** The session's existence
  is the truth today; the lobby list still says "Waiting for players" for a
  table mid-game. A `StartGame` refusal enum (not chess, not full, not seated)
  would let the screen say why a start did nothing; today it is an unset
  session.
- **Lobby verbs** (`JoinTable`, `TakeSeat`, `StandUp`, `LeaveTable`) on the
  lobby controller would replace `table_intents.ts` one function per call.
- **The catalogue.** `CreateTableDialog.tsx` hardcodes seat bounds that
  `GameSpecService.ListGameSpec` answers.
- **`ChessGame` is stored row, wire payload and view in one.** It grows with
  the game and is copied on every outcome. Fine for chess; the first thing to
  split for a game with a large state.
- **`ChessGame.resigningColor` duplicates `result.resigningPlayer.color`.**
