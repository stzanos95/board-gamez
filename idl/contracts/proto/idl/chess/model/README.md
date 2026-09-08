# idl/chess/model

The domain, as the library already understands it.

Proto package `idl.chess.model`; Python `from idl.chess.model.move_pb2 import Move`.

One message per dataclass in `packages/chess/src_python/chess/models`, one enum
per enum. These say what a thing *is*, and nothing about how it is stored or how
it is asked for. Everything else under `idl/chess/` is built out of them.

```
piece.proto     Color, PieceType, Occupant
square.proto    File, Rank, Square
castling.proto  CastlingSide, CastlingRight, CastlingRights
move.proto      MoveType, ParsedCoordinateMove, Move
board.proto     SquareOccupant, BoardState, PositionKey
game.proto      GameStatus, GameOutcome, ChessPlayer, PlayerRoster,
                ChessTurn, ChessTurnHistory, GameResult, ChessGame
```

These are the wire, not the domain. The library keeps its own models because
they carry behaviour — `Color.opponent`, `GameStatus.is_terminal`,
`Square.shifted` — and a generated class carries none. Converting between the
two is an adapter, named `<source>_to_<target>`.

Every file declares `option go_package` although Go is not a target: the OpenAPI
generator is a Go program that will not read a file without one. See the
toolchain notes in `idl/README.md`.

Two library types are deliberately absent. `Vector` is internal geometry and
never crosses a boundary. `AlgebraicMoveText` exists so notation cannot be
confused with coordinate text in Python; on the wire it is a named field on
`ChessTurn`, which cannot be confused with anything.
