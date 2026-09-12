# identity

Tracks the work that gives this system authenticated players, and the decisions
that work is built on. Written to be picked up cold, between sessions.

Read `ARCHITECTURE.md` first, then the skills each task names.

## What is wrong today

`player_id` is a field in the request body on every operation that acts for a
player. The browser mints it into `sessionStorage` and sends it. Nothing
verifies it, so a caller can send any id and take another player's seat, play
their turn, or leave their table.

`idl/contracts/proto/idl/identity/model/player.proto` already states the target:
a player is never carried in a request, and which player is acting comes from
the authenticated session.

`infra/compose/docker-compose.yml` publishes 50051 to the host, so the gRPC
server is reachable without passing the gateway at all.

## Decisions

Settled. Do not reopen these without a reason that is written down here.

### The identity provider is ours, brokering to Google over OIDC

No Keycloak. Keycloak would leave a `Player` row, friendships and the gateway's
session check still to write, and would add a second user store to reconcile
with ours.

What is written instead: an authorization-code + PKCE client against Google's
discovery document, and ID-token verification against Google's JWKS. There are
no passwords, no MFA and no token signing anywhere in this design.

`authlib` supplies both halves: `authlib.integrations.httpx_client.AsyncOAuth2Client`
for the code exchange, `authlib.jose` for the JWKS fetch and the claim checks.
`authlib.integrations.starlette_client` is not used — it carries its own
signed-cookie session, which would stand beside the session below as a second
answer to who is calling.

Another provider is a member of an enum, a file, and a config section. Keycloak,
if it is ever wanted, is one more implementation of `BaseIdentityProvider`.

### A session is opaque, held by the server, and carried in a cookie

`secrets.token_urlsafe(32)`, stored under the SHA-256 of the token so a dump of
the store yields no live session. Redis, with a TTL.

The cookie is `HttpOnly; Secure; SameSite=Lax`. Lax rather than Strict: the
OAuth callback is a top-level GET from Google, and a table link shared from
elsewhere has to arrive signed in. Every write is a POST carrying
`content-type: application/json`, which is what stands in for a CSRF token; a
double-submit token is the hardening to add if a write ever stops being a POST.

`deployables/gamez-ux/docker/nginx.conf` already serves the gateway and the
socket server same-origin, so the cookie needs no cross-site handling. A cookie
also reaches the WebSocket upgrade, which an `Authorization` header cannot.

### The viewer travels in transport metadata, held in a context variable

No operation gains a parameter. No generated file changes.

```
core/context/
├── viewer_context.py       ViewerContext(viewer_id) and the ContextVar holding it
└── transport/
    ├── http_viewer.py      ASGI middleware: cookie → session → set
    ├── grpc_viewer.py      server interceptor: metadata → set
    │                       client: read → attach metadata
    └── queue_viewer.py     envelope header → set
```

`ViewerContext` names a `viewer_id` and not a `player_id`, so `core` stays free
of any domain's vocabulary. A domain's adapter is what turns the viewer into the
`player_id` its controller takes.

The metadata key between the gateway and the server is `gamez-viewer-id`. The
server trusts it, which is only sound because 50051 is not reachable from
outside. Task 0 is what makes that true.

What to watch: a task started at bringup carries no viewer. `DeadlineTicker`
runs as nobody, which is correct, so nothing on that path may require one.
`asyncio.create_task` copies the context, so a task started inside a request
keeps the viewer.

### Guest players are real players

A visitor with no account gets a `Player` row and a session, the same as anyone
else. One code path: every request carries a session, every viewer is a stored
row.

Signing in with Google links the Google subject to the player that already
exists, so a guest who signs in keeps their tables.

### Authorization stays in the controllers

No policy engine, and no new layer. Every question of the form "may this player
do this here" is already answered by a controller with a typed outcome:
`NOT_A_PARTICIPANT`, `OUT_OF_TURN`, `NOT_OFFERED`, `NOT_SEATED`,
`NOT_AT_TABLE`. An engine would need the table and the session to answer any of
them, which puts the rules in a second place.

**This changes when moderators or administrators arrive.** A role that acts
across tables it is not seated at is not a rule any single controller owns, and
that is the point at which an authorization layer is worth its cost. Nothing
before then.

### Identity is stored in Redis

Players, credentials and sessions, behind `base_*_repository.py` in the four-file
provider shape. Postgres is a second registry entry when durability or a
friendship query asks for it; nothing above the repository changes when it
arrives.

### Testing with more than one player

A cookie is per-browser, so the two-tab trick in `README.md` stops working.
Incognito windows share one cookie jar however many are open, so incognito adds
one player and not N.

For N players on one machine: Firefox Multi-Account Containers, or N Chrome
profiles. Pick before task 4 and record it here.

## Deferred

Written down so they are not designed in by accident.

- **Private tables and invitations.** `Table` gains a visibility and a list of
  invited player ids — lobby vocabulary, so the lobby never learns what a friend
  is. The browser reads friends from identity and sends ids.
- **`FRIENDS_OF_OPENER` visibility.** The only part that needs a cross-domain
  question. The seam is a `BaseAdmission` in `lobby/controller/` beside
  `BaseSeating`, implemented by a package importing both `lobby` and `identity`,
  registered at bringup as `SeatingRegistry` is. Do not build before it is asked
  for.
- **Per-channel socket authorization.** `TableChanged` carries an id and a
  version, so an unauthenticated watcher learns nothing. Needed once a private
  table exists.
- **A viewer on a queue envelope.** No consumer acts for a viewer yet.

## Tasks

Status: `todo`, `doing`, `done`.

### 0. Stop publishing 50051 — `todo`

`infra/compose/docker-compose.yml`. The server trusts the viewer metadata the
gateway attaches; that trust requires the port to be unreachable from outside.
Decide what replaces it for `grpcurl` in local development.

### 1. The login screen — `todo`

**First task. No backend, no sign-in logic.**

A screen offering two things: continue with Google, and play as a guest. Google
is present and does nothing yet. Guest calls what
`packages/ux/src_tsx/identity/player_session.ts` already does, so behaviour is
unchanged behind a new door.

The screen is shown when there is no player, and the application is shown once
there is. `packages/ux/src_tsx/runtime/AppRoot.tsx` holds `PlayerProvider`;
`readOrCreatePlayer` currently mints on read, so minting has to become
deliberate for the screen to have anything to ask.

Load `frontend-development` and `typescript-style` first.

### 2. Schema — `todo`

Add `idl/identity/`: `model` (player, credential, session), `dto`, `obj`,
`service`. Remove and `reserved` the caller `player_id` from 18 request
messages:

| Package | Messages |
| --- | --- |
| `idl.lobby.dto` | `CreateTableRequest`, `JoinTableRequest`, `VacateSeatRequest`, `LeaveTableRequest` |
| `idl.game.dto` | `CreateSessionRequest`, `ReadSessionRequest`, `WithdrawPlayerRequest`, `ApplyCommandRequest` |
| `idl.chess.dto` | `ListSeatChoiceRequest`, `TakeSeatRequest`, `StartGameRequest`, `ReadGameRequest`, `PlayActionRequest` |
| `idl.uno.dto` | the same five |

`idl.lobby.dto.ListSeatChoiceRequest.player_id` stays. `SeatingService` is
declared and not served, and that field is the subject being asked about rather
than the caller.

`breaking.sh` refuses a field removal against `main`. Decide how that is handled
and record it here.

The OAuth pair is hand-written and the first `external` paths in the system,
because both answer with a redirect rather than a body:

```
GET /external/platform/identity/google/start
GET /external/platform/identity/google/callback
```

Load `modeling` first. Do not run the generator.

### 3. `packages/identity` — `todo`

Controllers for player, session, credential and sign-in. Three repositories in
the provider shape. The guest path end to end, with no Google yet.

One line each in `grpc-server` and `fastapi-gateway` at bringup.

Load `backend-development` and `python-style` first.

### 4. Viewer context — `todo`

`core/context/` as above. The gateway's middleware, the server's interceptor,
the outbound metadata on every gRPC client. Each domain's adapter gains
`context_to_player_id`, replacing the `*_request_to_player_id` it has now. No
controller signature changes.

### 5. The browser reads a session — `todo`

`player_session.ts` becomes a call to identity rather than a read of
`sessionStorage`. `fetch` gains `credentials: "same-origin"`. Every
`playerId` argument leaves the gateway calls.

### 6. Google — `todo`

`GoogleIdentityProvider`, the two redirect routes, and linking a Google subject
to a player that already exists.

The client secret is named by a path in the config file, never a value in it,
and never read from the environment.

### 7. Friends — `todo`

`FriendController` and its repository. Request, accept, decline, remove, list.

## Open

- What replaces published 50051 for local `grpcurl` (task 0).
- How the breaking change in task 2 is landed (task 2).
- Which browser arrangement is used for N players (before task 4).
- Whether a guest player with no table history expires.
