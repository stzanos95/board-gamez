# gamez-ux

The browser entry point. Owns its environment and its settings: the bundler, the
image, the web server and the config file all live here.

## Layout

```
config/       the JSON the app is brought up from
docker/       the image: a node build, then nginx
scripts/      running on this machine, without installing node
src_tsx/      main.tsx, and nothing else
index.html    the one page
vite.config.ts
```

`main.tsx` fetches the settings document, then mounts `AppRoot` with it. Every
screen, hook and component belongs to [`packages/ux`](../../packages/ux), so
adding one never touches this deployable.

## Every tab is a player

There is no sign-in yet. A player identifier is minted per browser tab and kept
in session storage, so **opening a second tab is joining as a second player** and
a table can be filled from one browser.

Reloading a tab keeps its player. Closing it ends them.

When authentication arrives it replaces one file,
`packages/ux/src_tsx/identity/player_session.ts`, and the calls it feeds are
already same-origin — nginx forwards them — so a session cookie needs no
cross-origin arrangement.

## Settings

Brought up from `config/gamez_ux.json`, fetched before anything renders.
**Nothing in this app reads a build-time variable.**

```json
{
  "gateway": { "baseUrl": "/api", "requestTimeoutMs": 8000 },
  "socket": { "baseUrl": "/ws", "reconnectDelayMs": 1000, "maxReconnectDelayMs": 30000 },
  "theme": "midnight",
  "freshness": {
    "staleTimeMs": 2000,
    "lobbyIntervalMs": 10000,
    "tableIntervalMs": 3000,
    "gameIntervalMs": 2000
  },
  "chess": { "defaultSkin": "classic" }
}
```

- `theme` names a theme in `packages/ux/src_tsx/theme/theme_registry.ts`.
  `midnight` and `daylight` ship. Changing this line changes the whole interface.
- `socket` is where changes are announced from. A socket that drops is
  reopened after `reconnectDelayMs`, doubling on each failure up to
  `maxReconnectDelayMs`.
- The intervals are polling, which runs only while the socket that would
  announce a change is not open, and never while the tab is hidden.
- A field that is missing, of the wrong type, or naming a theme that does not
  exist stops bringup with a message. Nothing falls back to a default.

The document is served beside the bundle, so a container runs against another
gateway by mounting a different file over
`/usr/share/nginx/html/gamez_ux.json` — no rebuild.

## Calls to the gateway, and the socket

The browser calls `/api/…` on its own origin, and that prefix is forwarded to the
gateway; it opens sockets under `/ws/…`, forwarded to the socket server. Both
are forwarded by the dev server here and by nginx in the container. The
application therefore makes no cross-origin request, and neither upstream
needs an origin allowed.

The path after the prefix is the path the `.proto` declares. Nothing writes it
down.

## Running

Nothing has to be installed on this machine. The node toolchain is a container.

```bash
scripts/local-dev.sh        # http://127.0.0.1:5173
scripts/local-build.sh      # type-check, then bundle into dist/
scripts/local-typecheck.sh
scripts/npm.sh install      # runs at the workspace root
```

The dev server forwards to a gateway on `127.0.0.1:8080`, so start one first:

```bash
../fastapi-gateway/scripts/local-serve.sh
```

In a container, from [infra/](../../infra/):

```bash
../../infra/scripts/up.sh    # http://127.0.0.1:8081
```

## The workspace

The TypeScript side is one npm workspace, rooted at the repository:
`idl/contracts/gen/typescript`, `packages/ux`, and this deployable. One install
puts a single copy of React, MUI and the contracts where all three resolve them.

`@board-gamez/idl` is consumed as a package, through the export map its
generator writes. `@board-gamez/ux` is compiled from source instead: its modules
are a mix of `.ts` and `.tsx`, and one export pattern cannot name both
extensions. `tsconfig.json` and `vite.config.ts` carry that one mapping.
