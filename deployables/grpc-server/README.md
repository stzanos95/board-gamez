# grpc-server

The internal gRPC services of the platform. Owns its environment and its
settings: the image, the entrypoint, the dependency set and the config file all
live here.

## Layout

```
config/       the YAML the app is brought up from
docker/       Dockerfile and the entrypoint that knows how to run anything
scripts/      running on this machine, without a container
src_python/   main.py, plus the grpc_server package
tests/        the server's own tests
```

```
grpc_server/
├── service_host_config.py       the settings, as dataclasses
├── service_host.py              the gRPC server, the servicers on it, and the deadline tick
├── platform_controllers.py      the controllers every hosted game shares
├── products/
│   ├── base_hosted_product.py   what a game supplies to be hosted
│   ├── chess_hosted_product.py  chess: its rules, its seating, its servicers
│   └── hosted_products.py       every game this process hosts
└── log_level.py                 the levels the logging module accepts
```

`main.py` reads the configuration file named on the command line and hands it to
`ServiceHost`, which builds the server, registers the servicers, starts the
tick that expires a game's deadlines, and serves. Each of those is its own
method, so a change to one is a change to one.

## Services

The server declares none of its own. A domain package publishes a ready-made
servicer, generated from the schema, and bringup registers it:

```python
LobbyServicers.add_table_service(server, controllers.tables)
```

Adding a domain is a dependency and one more line. No message, no method and no
handler is written here — those belong to the schema and to the domain that owns
them.

A game is a product, and a product is one `BaseHostedProduct` in `products/`:
its game type, the rules the session controller asks, the seating the lobby
asks, and the servicers it answers. `HostedProducts.build` lists them, and
bringup fills the rules registry and the seating registry from that list and
registers each product's servicers after the platform's. Adding a game is a
dependency in `pyproject.toml`, one file in `products/`, and one entry in
`HostedProducts`. See `.claude/skills/adding-a-game/`.

Registration mutates the server and answers the service's full name, which is
what gRPC offers in place of the router an HTTP framework returns. The names come
back so reflection can publish them without spelling any of them out again.

## Transport

The listener speaks plain HTTP/2 without TLS. This process is reachable only
from inside, and every path it serves is under `/internal`, so transport security
is terminated ahead of it.

Reflection is on by default, which is this server's answer to the gateway's
`/openapi.json`: a client can list and call services without a copy of the
`.proto` files.

```bash
grpcurl -plaintext 127.0.0.1:50051 list
grpcurl -plaintext 127.0.0.1:50051 list idl.lobby.service.TableService
```

## Stopping

A container stops its process with a signal. `SIGINT` and `SIGTERM` both begin a
graceful shutdown: the listener closes, calls already in flight have
`graceful_shutdown_seconds` to finish, and anything still running when that
elapses is cancelled.

## Settings

Brought up from a YAML file parsed into `ServiceHostConfig` by a mashumaro YAML
mixin. **Nothing in this app reads the environment.**

`--config` is required and has no default. Which file to run with is chosen
outside the process — by `scripts/local-serve.sh` here, and by
`docker/entrypoint.sh` in a container — so nothing has to guess where it is
deployed. `config/grpc_server.yaml` is what both of them name.

```yaml
application:
  name: board-gamez grpc server
  version: "0.1.0"
server:
  host: "0.0.0.0"
  port: 50051
  log_level: info
  maximum_concurrent_rpcs: 256
  max_receive_message_bytes: 4194304
  max_send_message_bytes: 4194304
  graceful_shutdown_seconds: 10
  reflection: true
```

Run with different settings by pointing at another file:

```bash
scripts/local-serve.sh --config /path/to/your.yaml
```

Parsing is mashumaro's. A missing file, a missing field, a malformed document or
a log level that does not exist raises where it happens, and the process stops
before anything listens.

## Running

On this machine (needs `uv` — run `./setup.sh` at the repository root):

```bash
scripts/local-serve.sh
scripts/local-test.sh
scripts/lock.sh          # rewrite uv.lock using uv inside a container
```

In a container, from [infra/](../../infra/):

```bash
../../infra/scripts/serve.sh
../../infra/scripts/test.sh
../../infra/scripts/lint.sh
```
