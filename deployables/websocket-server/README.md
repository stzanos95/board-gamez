# websocket-server

The socket a browser is told over that something changed. Owns its environment
and its settings: the image, the entrypoint, the dependency set and the config
file all live here.

## Layout

```
config/       the YAML the app is brought up from
docker/       Dockerfile and the entrypoint that knows how to run anything
scripts/      running on this machine, without a container
src_python/   main.py, plus the websocket_server package
tests/        the server's own tests
```

```
websocket_server/
├── websocket_server_config.py       the settings, as dataclasses
├── websocket_server.py              bringup: sources, controller, routes, run
├── log_level.py                the levels the logging module accepts
├── controller/
│   ├── base_client.py          what any connected client answers: send(bytes)
│   ├── client_hub.py           every open connection, by the channel it watches
│   └── subscription_controller.py
│                               subscribes every source while a channel is
│                               watched; relays what arrives to the watchers
├── adapters/
│   ├── event_adapters.py       an event, to the frame a browser is sent
│   └── route_adapters.py       a request or a socket, to what a route needs
└── service/
    ├── socket_routes.py        /ws/lobby and /ws/tables/:table_id
    ├── channel_names.py        the channel each route watches
    ├── websocket_behavior.py   the mapping socketify takes for a route
    ├── socket_connection.py    what a socket carries from upgrade to close
    ├── socketify_client.py     a client over a socketify socket
    ├── socketify_types.py      the surface of socketify used, as protocols
    └── upgrade_headers.py      the handshake headers an upgrade carries over
```

`main.py` reads the configuration file named on the command line and hands it
to `WebsocketServer`, which builds one consumer per configured source, the controller
over them, declares the two routes, and serves.

## What travels

Every write that succeeds is published as an event in a
`idl.core.dto.QueueMessageEnvelope`, on the channel of the table it concerns
(`table:<table_id>`) and, for the events the lobby list needs, on `lobby` as
well. This server subscribes a channel on every source while at least one
socket watches it, and unsubscribes it when the last one leaves.

A browser is never sent an event. Each event is opened only to read an id and a
version, and becomes one frame, a `idl.core.dto.WebsocketMessageEnvelope`
carrying:

```
idl.lobby.model.TableChanged   { table_id,   version }   every table event; TableClosed is version 0
idl.game.model.SessionChanged  { session_id, version }   every game event
```

sent as bytes to every socket watching the channel the event arrived on. A
browser compares the version with what it holds and re-reads through the typed
service it renders from. An event of a type this build does not know is
dropped.

```
GET /ws/tables/{table_id}   TableChanged and SessionChanged for that table
GET /ws/lobby               TableChanged for every table
```

A browser sends nothing over these sockets. There is no message handler; a
frame that arrives is dropped by the library, and the server pings on its own
so an idle socket stays open.

## Sources

`sources` in the configuration is a list of `core.queue` `QueueConfig`
sections. Each is built once through `QueueProvider.get_consumer`, and the
controller holds them as `BaseQueueConsumer`s: it subscribes every one of them
to a watched channel and relays what any of them yields. Nothing here names a
broker. One Redis source is what ships; a second source is one more list entry.

## Transport

socketify: uWebSockets under an asyncio event loop, in one process and one
thread. The consumers run on that loop, so a frame is sent from the task that
read the event, with nothing in between.

The library ships no type information. `service/socketify_types.py` models the
surface this server uses as protocols, and every handler is typed against them.
Its native library is linked against libuv, which the wheel does not carry:
the image installs `libuv1`, and running on this machine needs
`sudo apt-get install libuv1t64` (`./setup.sh` reports when it is missing).

## Stopping

`SIGINT` and `SIGTERM` both stop the server the same way: the listener closes,
the relays are cancelled, and every source is closed. `SIGTERM` reaches the
handler this server installs on the loop, and `run` returns. `SIGINT` reaches
the handler the library installs when `run` begins, which closes the listener
and raises `SystemExit`; the shutdown runs from a `finally` around `run`, so
both paths release the sources before the process ends.

## Settings

Brought up from a YAML file parsed into `WebsocketServerConfig` by a mashumaro YAML
mixin. **Nothing in this app reads the environment.**

`--config` is required and has no default. Which file to run with is chosen
outside the process — by `scripts/local-serve.sh` here, and by
`docker/entrypoint.sh` in a container. `config/websocket_server.yaml` is what
the script names and `config/websocket_server.container.yaml` what the image
names; they differ only in the broker's hostname.

```yaml
application:
  name: board-gamez websocket server
  version: "0.1.0"
server:
  host: "0.0.0.0"
  port: 8082
  log_level: info
  idle_timeout_seconds: 120
  max_payload_bytes: 1024
sources:
  - queue: redis
    redis_config:
      host: "127.0.0.1"
      port: 6379
      database: 0
      channel_prefix: "gamez"
```

`channel_prefix` is set together with the publisher's. An empty `sources` is
refused at bringup.

## Running

On this machine (needs `uv` and libuv — see Transport):

```bash
scripts/local-serve.sh
scripts/local-test.sh
scripts/lock.sh          # rewrite uv.lock using uv inside a container
```

In a container, from [infra/](../../infra/), `up.sh` brings it up on 8082
beside the rest of the stack. To watch a table's frames arrive:

```bash
websocat --binary ws://127.0.0.1:8082/ws/tables/<id> | xxd
```
