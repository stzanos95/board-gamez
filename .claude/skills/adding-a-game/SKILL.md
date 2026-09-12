---
name: adding-a-game
description: Every file a new game touches, in the order they are written, with the chess file to copy beside each one. Load before adding a game to the platform — a new GameType, a rules package, a product package, the entries in both deployables, and the screens in the browser. Covers the design questions a game answers before its schema is written and which BaseRules method each answer lands in, the names a game takes in each language, the schema it declares, the two packages, the one file per deployable, the build and check wiring, the five browser records, and the tests each layer carries.
---

# Adding a game

These rules address whoever writes the code, a developer or an assistant. A
step a rule leaves to "the user" — running the generator, committing — is the
developer's own when they work alone.

A game is added, never wired in. `packages/game` and `packages/lobby` do not
change. Every step below is a new file or an entry in a list that exists for
this purpose, and chess is the reference: each row names the chess file to
read before writing the same file for the new game.

The skills that govern each step still apply and are loaded first: `modeling`
for the schema, `python-style` and `backend-development` for the packages and
deployables, `typescript-style` and `frontend-development` for the browser.

## 1. Answer the design questions first

The platform asks a game six questions through `BaseRules`
(`packages/game/src_python/game/controller/base_rules.py`) and one through
`BaseSeating` (`packages/lobby/src_python/lobby/controller/base_seating.py`).
Each row below is settled before the schema is written, because the answer
decides what the schema carries. Chess has no hidden information, no chance,
no clock and one actor at a time, so copying chess answers none of those four.

| Question | Where the answer lands | Chess |
| -------- | ---------------------- | ----- |
| How many play? A fixed number, or a range? | `read_bounds` answers `ParticipantBounds`. `create_game` refuses a count outside them | Exactly 2 |
| Does a participant have a role the game must know — a colour, a token, a faction? | The product packs it into `Participant.role` as `Any` in one adapter, and `BaseSeating.list_seat_choices` offers each open seat with the role it carries | Yes: `ChessSide` |
| Who may act on a state? One at a time, or several? | Every `GameState` names `participants_to_act`. Several means each named participant may write, and the first to write moves the version the rest re-read | One |
| Is any information hidden from some viewers? | `read_view` projects the state for a participant; participant 0 is a spectator. The view type and the state type are then two messages | No: the view is the state |
| Does the game draw on chance? | `create_game` receives a `seed`; the state carries what the sequence needs to continue. The rules call no random source of their own | No |
| Does a state expire — a clock, a turn timer? | The state sets `acts_within`; `expire_deadline` answers what the state becomes. A game with no clock sets nothing and answers `None` | No |
| What does leaving do to the game? | `withdraw_participant` answers the state after the participant is gone. It is asked in or out of turn and never once there is a result | The leaver resigns |
| How does the game end, and how does each participant come out? | The state carries a `GameResult` once it is over, one `ParticipantResult` per participant. A scored game says its score in its own state | Win, loss, draw |

Write the answers down in the reply or the pull request, one line each. An
answer that changes later changes the schema, and a schema change after
generation is a migration.

## 2. The names a game takes

One word, `<game>`, spelt the same way in every language. The columns are
fixed; only the word changes.

| Where | Name | Chess |
| ----- | ---- | ----- |
| Enum member | `GAME_TYPE_<GAME>` in `idl/game/model/game_type.proto` | `GAME_TYPE_CHESS` |
| Schema domain | `idl/contracts/proto/idl/<game>/` | `idl/chess/` |
| Proto package | `idl.<game>.model`, `.dto`, `.service` | `idl.chess.model` |
| Service | `<Game>Service` | `ChessService` |
| Endpoint paths | `/internal/product/<game>/<method>/<entity>` | `/internal/product/chess/play/action` |
| Rules package | `packages/<game>/`, distribution `<game>-game`, import `<game>` | `packages/chess/`, `chess-game`, `chess` |
| Product package | `packages/product-<game>/`, distribution `product-<game>`, import `product_<game>` | `packages/product-chess/`, `product-chess`, `product_chess` |
| Product classes | `<Game>Rules`, `<Game>Seating`, `<Game>SessionController`, `Grpc<Game>Service`, `Http<Game>Service`, `Grpc<Game>Client`, `Product<Game>Servicers`, `Product<Game>Routers` | `ChessRules`, … |
| Server product | `deployables/grpc-server/src_python/grpc_server/products/<game>_hosted_product.py`, class `<Game>HostedProduct` | `chess_hosted_product.py` |
| Gateway product | `deployables/fastapi-gateway/src_python/fastapi_gateway/products/<game>_gateway_product.py`, class `<Game>GatewayProduct` | `chess_gateway_product.py` |
| Browser modules | `packages/ux/src_tsx/<game>/` | `packages/ux/src_tsx/chess/` |
| Browser components | `packages/ux/src_tsx/components/<game>/` | `components/chess/` |
| Browser enum member | `GameType.<GAME>` | `GameType.CHESS` |

## 3. The schema

Load `modeling` before this step. Everything here is under
`idl/contracts/proto/idl/`.

| Write | What it declares | Chess |
| ----- | ---------------- | ----- |
| `game/model/game_type.proto` | One new member. Never renumber the others | `GAME_TYPE_CHESS = 1` |
| `<game>/model/*.proto` | The rules' vocabulary: every noun the rules compute over, one message per noun and one enum per closed set. The rules package declares none of these again | `board.proto`, `move.proto`, `piece.proto`, `square.proto` |
| `<game>/model/action.proto` | What a participant does in one action. A `oneof` over the kinds | `ChessAction`: a move or a resignation |
| `<game>/model/game.proto` | The game's own state as the platform stores it opaquely. Everything `apply_action` needs and nothing it recomputes | `ChessGame` |
| `<game>/model/<role>.proto` | The role a seat carries, when the game has roles. Packed into a seat and a participant as `Any` | `side.proto`: `ChessSide` |
| `<game>/model/session.proto` | The platform's session with the game opened and the viewer named in the game's terms, and `ActionResult` carrying a `CommandOutcome` beside it | `ChessSession`, `ActionResult` |
| `<game>/model/table.proto` | The lobby's table with every seat's role opened, a seat choice with its role opened, the collection, and the seat result | `ChessTable`, `ChessSeatChoice`, `ChessSeatChoiceCollection`, `ChessSeatResult` |
| `<game>/dto/table.proto` | Requests and responses for reading the table, listing seat choices, taking a seat | as named |
| `<game>/dto/game.proto` | Requests and responses for starting, reading and playing | as named |
| `<game>/service/game.proto` | `<Game>Service` with these six RPCs, each under `/internal/product/<game>/…`: `ReadTable`, `ListSeatChoice`, `TakeSeat`, `StartGame`, `ReadGame`, `PlayAction` | `ChessService` |

The six RPCs are the minimum, not a suggestion. The browser never packs an
`Any`, and the gateway translates only the payload types a product declares,
so a game with no service of its own cannot be played. A game with hidden
information declares a view message beside its state, and `ReadGame` answers
the view.

`<game>` imports `game` and `lobby`. `game` and `lobby` import nothing under
`<game>`. `buf lint` enforces the naming; `breaking.sh` enforces the numbering.

Then the developer runs `./idl/scripts/generate.sh` and commits
`idl/contracts/gen` with the schema. `./idl/scripts/check.sh` refuses drift
between the two.

## 4. The rules package: `packages/<game>/`

Pure computation over `idl.<game>.model`. No I/O, no configuration, nothing
from `idl.game`, nothing about participants or sessions. It is callable from a
test with nothing running.

| Write | What it is | Chess |
| ----- | ---------- | ----- |
| `pyproject.toml` | Copy chess's. Depends on `board-gamez-idl` by relative path and nothing else | `packages/chess/pyproject.toml` |
| `src_python/<game>/py.typed` | Empty marker, so consumers type-check against it | |
| `src_python/<game>/core/` | Static lookups over the schema's values, named for the plural of the noun | `colors.py`: `Colors.opponent` |
| `src_python/<game>/engine/` | The game: a new state from an action, the legal actions, whether it is over and how | `chess_engine.py` |
| `src_python/<game>/adapters/` | Between the schema's record of a game and whatever the engine computes over, when they differ. Reading a record back recomputes what it derives | `game_adapters.py`, `board_adapters.py` |
| `tests_python/` | The rules, exhaustively. The test that catches the most is the one that counts outcomes against a published total | `perft/` |

A layering that fits chess — pieces, movement, a board — is chess's. A card
game or a dice game has its own; what does not change is that every type is
the schema's and the package never prints.

## 5. The product package: `packages/product-<game>/`

The only package importing both `game` and `<game>`. Load
`backend-development` before this step; every file is in the layer that skill
names. `pyproject.toml` is chess's with the names changed: it depends on
`idl-fastapi`, `board-gamez-idl`, `core`, `<game>-game`, `game` and `lobby`.

| Write | Layer | What it does | Chess |
| ----- | ----- | ------------ | ----- |
| `controller/<game>_rules.py` | Business | `BaseRules` for this game. Decides what a participant number means, refuses a wrong count, refuses an action out of turn or not legal, answers `read_view`, `withdraw_participant`, `expire_deadline`, `read_bounds` | `chess_rules.py` |
| `controller/<game>_seating.py` | Business | `BaseSeating`. Which open seats a player may take and with which role. Writes nothing | `chess_seating.py` |
| `controller/<game>_session_controller.py` | Business | Composes `TableController`, `SeatController` and `SessionController`. Answers every `<Game>Service` operation in the game's own types: reads the table with roles opened, lists and takes seat choices, decides who may start, plays an action | `chess_session_controller.py` |
| `adapters/<game>_rules_adapters.py` | Adapter | `GameState` ↔ the game's state message, `Action` → the game's action, `ParticipantRole`s → whatever the engine is built from, and every `RulesService` request and response | `chess_rules_adapters.py` |
| `adapters/<game>_seat_adapters.py` | Adapter | The one place a role is packed and opened. `Table` → `<Game>Table`, `SeatChoice` ↔ `<Game>SeatChoice`, `SeatResult` → `<Game>SeatResult`, and every seat request and response in both protobuf and pydantic | `chess_seat_adapters.py` |
| `adapters/<game>_session_adapters.py` | Adapter | `SessionView` → `<Game>Session`, `CommandResult` → `ActionResult`, the action into a payload, and every game request and response in both protobuf and pydantic | `chess_session_adapters.py` |
| `service/grpc_rules_service.py` | Service | `RulesServiceServicer` over `<Game>Rules`: adapt, call, adapt | as named |
| `service/grpc_<game>_service.py` | Service | `<Game>ServiceServicer` over `<Game>SessionController`: adapt, call, adapt | `grpc_chess_service.py` |
| `service/grpc_<game>_client.py` | Service | The stub the gateway calls the server through. Built unconnected, dialled by `connect` | `grpc_chess_client.py` |
| `service/http_<game>_service.py` | Service | The generated router's base over the client: call, hand back | `http_chess_service.py` |
| `service/product_<game>_servicers.py` | Service | `add_rules_service` and `add_<game>_service`: register on a server and answer the full name | `product_chess_servicers.py` |
| `service/product_<game>_routers.py` | Service | `<game>_service(client)`: the router the gateway includes | `product_chess_routers.py` |

Every `__init__.py` is empty. `RulesService` is served so a tool can reach
the rules through the server; the session controller calls the same object
in-process. `SeatingService` is declared in the schema and served by no
product; the lobby asks `BaseSeating` in-process.

Tests: `tests_python/test_<game>_rules.py` drives `BaseRules` with packed
actions and asserts on the state and the result;
`tests_python/test_<game>_session_controller.py` builds the platform's
controllers over in-memory repositories and an in-memory publisher and plays a
game through the product. The fakes are copied into the package's own `tests_python/`, one per
package, never imported across packages — see chess's `in_memory_repositories.py`,
`in_memory_queue_publisher.py`, `fixed_clock.py` and `chess_actions.py`.

## 6. The server: `deployables/grpc-server/`

| Edit | What | Chess |
| ---- | ---- | ----- |
| `pyproject.toml` | Add `product-<game>` to `dependencies` and to `[tool.uv.sources]` by relative path, then `scripts/lock.sh` | `product-chess` |
| `src_python/grpc_server/products/<game>_hosted_product.py` | `BaseHostedProduct`: builds the rules and the seating in `__init__`, answers the game type, and registers the product's servicers over the platform's controllers | `chess_hosted_product.py` |
| `src_python/grpc_server/products/hosted_products.py` | One entry in `HostedProducts.build` | |
| `tests/test_service_host.py` | The registered names now include the product's | |

Nothing else changes. `service_host.py` fills the rules registry and the
seating registry from the list and registers each product after the platform.

## 7. The gateway: `deployables/fastapi-gateway/`

| Edit | What | Chess |
| ---- | ---- | ----- |
| `pyproject.toml` | Add `product-<game>` the same way, then `scripts/lock.sh` | `product-chess` |
| `src_python/fastapi_gateway/products/<game>_gateway_product.py` | `BaseGatewayProduct`: holds the client, dials and closes it, answers the router, and answers the schema files declaring every type the game packs into a payload — the action, the state, the role | `chess_gateway_product.py` |
| `src_python/fastapi_gateway/products/gateway_products.py` | One entry in `GatewayProducts.build` | |
| `tests/test_gateway_api.py` | A path of the product is served, and a packed type of the product is translatable | |

A payload type left out of `get_payload_files` cannot be sent or answered as
JSON. The failure is a translation error at request time, so the test is what
catches it.

## 8. Build and checks

| Edit | What |
| ---- | ---- |
| `.pre-commit-config.yaml` | Two `mypy-*` hooks and two `pytest-*` hooks, in the same shape as the others, for `packages/<game>` and `packages/product-<game>`. A project with no hook is checked nowhere |
| `setup.sh` | Two `ensure_project_environment` lines, so `./setup.sh` builds their environments |

The Dockerfiles copy `packages/` whole and `./infra/scripts/test.sh` runs
every package's suite through the gateway image, so neither changes.

## 9. The browser: `packages/ux/`

Load `frontend-development` and `typescript-style` before this step. Five
records are keyed by `GameType`, and the build fails until each has the new
member. That is the whole point of them: find them by the compile error.

| Edit | What | Chess |
| ---- | ---- | ----- |
| `src_tsx/lobby/table_labels.ts` | `GAME_TYPE_LABELS`: the name shown. `CREATABLE_GAME_TYPES`: add the member when a table of it may be opened from the lobby | `"Chess"` |
| `src_tsx/components/common/GameArtwork.tsx` | `ARTWORK_BY_GAME_TYPE`: a component drawing the game's picture | `ChessArtwork` |
| `src_tsx/components/table/GameScreen.tsx` | `SCREEN_BY_GAME_TYPE`: the screen the game is played on, taking `GameScreenProps` | `ChessScreen` |
| `src_tsx/runtime/game_change_keys_registry.ts` | `CHANGE_KEYS_BY_GAME_TYPE`: which queries a `TableChanged` or `SessionChanged` frame reaches | `CHESS_CHANGE_KEYS` |
| `src_tsx/runtime/packed_types.ts` | `PACKED_FILES_BY_GAME_TYPE`: the generated files declaring every type the game packs — at least the role | `CHESS_PACKED_FILES` |

Then the game's own directory, in the same shape as `src_tsx/chess/`:

| Write | What | Chess |
| ----- | ---- | ----- |
| `<game>/<game>_gateway.ts` | One method per `<Game>Service` operation, built from the generated service descriptor | `chess_gateway.ts` |
| `<game>/<game>_queries.ts` | The query keys | `chess_queries.ts` |
| `<game>/<game>_change_keys.ts` | The `GameChangeKeys` the registry entry names | `chess_change_keys.ts` |
| `<game>/<game>_packed_types.ts` | The `DescFile`s the registry entry names | `chess_packed_types.ts` |
| `<game>/<game>_views.ts`, `seat_views.ts` | Pure functions from the generated messages to what a component draws | `chess_views.ts` |
| `<game>/<game>_labels.ts` | Records from the game's enums to text | `chess_labels.ts` |
| `<game>/use_*.ts` | One hook per query or mutation: the table, the seat choices, the session, taking a seat, starting, playing | `use_chess_session.ts`, `use_play_action.ts` |
| `components/<game>/` | Rendering only: values and callbacks in, elements out | `ChessScreen.tsx` |

A setting the game needs at bringup — a default skin — is a section in
`deployables/gamez-ux/config/gamez_ux.json` read by `src_tsx/config/ux_config.ts`.
A game with no such setting adds nothing there.

## 10. Run it

```bash
uv run --directory packages/<game> python -m pytest
uv run --directory packages/product-<game> python -m pytest
uv run --directory deployables/grpc-server python -m pytest
uv run --directory deployables/fastapi-gateway python -m pytest
./deployables/gamez-ux/scripts/local-typecheck.sh
./infra/scripts/test.sh
./infra/scripts/up.sh
```

Then open two tabs, create a table of the new game, take both seats, start,
and play to a result. `grpcurl -plaintext 127.0.0.1:50051 list` shows the
product's service; `curl http://127.0.0.1:8080/openapi.json` shows its paths.

## Checklist

- [ ] Every design question in section 1 is answered in writing, before the schema
- [ ] The names in section 2 are used as given, in every language
- [ ] `<Game>Service` declares the six RPCs under `/internal/product/<game>/`
- [ ] `idl/contracts/gen` is regenerated and committed with the schema
- [ ] `packages/<game>` imports nothing from `idl.game` and performs no I/O
- [ ] `packages/product-<game>` is the only package importing both `game` and `<game>`
- [ ] A role is packed and opened in one adapter, and nowhere else
- [ ] One product file and one list entry in each deployable; `service_host.py` and `gateway_api.py` are untouched
- [ ] Every packed type is in `get_payload_files` and in `PACKED_FILES_BY_GAME_TYPE`
- [ ] Two mypy hooks, two pytest hooks and two `setup.sh` lines
- [ ] The five browser records compile
- [ ] Every suite in section 10 passes, and a game was played in a browser to a result
