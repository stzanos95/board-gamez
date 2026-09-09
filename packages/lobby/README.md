# lobby

The routers a lobby answers over HTTP, and the class that answers them.

```
src_python/lobby/service/
├── lobby_routers.py         what a gateway includes
└── http_table_service.py    answers each operation, over HTTP
```

The paths, the request models and the response models are not written here. They
are generated from `idl/contracts/proto` into `idl-fastapi`, and
`TableServiceRouter.build` binds them to an implementation:

```python
application.include_router(LobbyRouters.table_service())
```

`HttpTableService` is where the call to the lobby goes. Every method raises
`NotImplementedError` — a body that must return a typed response cannot be left
as `pass`.

## Running the tests

```bash
uv run python -m unittest discover -s tests_python -t .
```
