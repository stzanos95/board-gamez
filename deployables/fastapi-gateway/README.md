# fastapi-gateway

The HTTP entry point to the platform. Owns its environment and its settings: the
image, the entrypoint, the dependency set and the config file all live here.

## Layout

```
config/       the YAML the app is brought up from
docker/       Dockerfile and the entrypoint that knows how to run anything
scripts/      running on this machine, without a container
src_python/   main.py, plus the fastapi_gateway package
tests/        the gateway's own tests
```

```
fastapi_gateway/
├── gateway_api_config.py   the settings, as dataclasses
├── gateway_api.py          the FastAPI application and the server around it
└── log_level.py            the levels uvicorn accepts
```

`main.py` reads the configuration file named on the command line and hands it to
`GatewayAPI`, which builds the application, builds the server around it, and
serves. Each of those is its own method, so a change to one is a change to one.

## Routes

None yet. The application is built empty; the routes arrive as generated stubs
from `idl/contracts/gen/openapi`.

FastAPI still serves `/openapi.json`, `/docs` and `/redoc`, which is enough to
see that a deployment is up and reporting the version it was configured with.

## TLS

The listener speaks plain HTTP. TLS is terminated ahead of this process, so the
scheme and client address of the original request arrive in forwarded headers.
They are read only when `proxy_headers` is true, and only from the addresses
`forwarded_allow_ips` names — anything else may set those headers freely.

## Settings

Brought up from a YAML file parsed into `GatewayAPIConfig` by a mashumaro YAML
mixin. **Nothing in this app reads the environment.**

`--config` is required and has no default. Which file to run with is chosen
outside the process — by `scripts/local-serve.sh` here, and by
`docker/entrypoint.sh` in a container — so nothing has to guess where it is
deployed. `config/fastapi_gateway.yaml` is what both of them name.

```yaml
application:
  title: board-gamez gateway
  version: "0.1.0"
  root_path: ""
server:
  host: "0.0.0.0"
  port: 8080
  log_level: info
  access_log: true
  proxy_headers: true
  forwarded_allow_ips: "127.0.0.1"
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
curl http://127.0.0.1:8080/openapi.json
```

In a container, from [infra/](../../infra/):

```bash
../../infra/scripts/serve.sh
../../infra/scripts/test.sh
../../infra/scripts/lint.sh
```
