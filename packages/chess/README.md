# chess-game

A chess engine. Full rules, no interface: it reads positions and answers questions
about them. Zero dependencies, and no `print` or `input` anywhere in the package.

The import name is `chess`. It ships a `py.typed` marker, so consumers type-check
against it properly.

## Layering

```
core → contracts → movement → pieces → board → rules → notation → engine
                                                                    ↕ adapters
```

Every type is the schema's: a square, a move, a piece, a position and a game
are `idl.chess.model` messages and enums, and this package declares none of
its own for anything the schema names.

- **`core`** depends on nothing: board dimensions, the error hierarchy, and
  static lookups over the schema's values — `Colors.opponent`,
  `Squares.shifted`, `MoveTypes.is_capture`.
- **`contracts`** is `BoardStateView`, the read-only face a piece is handed.
- **`adapters`** converts between the schema's record of a position or a game
  and the board and engine that compute over it. Reading a game back recomputes
  the legal moves and the status from the position.
- Everything else is behaviour.

## Where the rules live

Two tiers, and the division is the central design decision.

**Pieces own geometry and whatever they can decide from where they stand.** A
piece is handed a `BoardStateView` and returns `tuple[Move, ...]`. Pawns own the double
push, en passant and promotion, because each needs only the pawn's own square plus
one fact the board already publishes. Pieces never change anything.

**The rules layer owns everything that needs the whole board.** Check, pins,
castling and game termination. `LegalMoveGenerator` gathers what the pieces offer,
adds castling, and discards any move that would leave its own king in check.

Castling is generated in `rules/castling_rule.py` rather than by the king, because
"the king may not pass through an attacked square" needs the full enemy attack map.
That keeps `King` a plain one-step-in-eight-directions piece.

Legality is decided by playing a move and looking at the result. Pins, discovered
checks and a king retreating along a checking ray all fall out of that with no
special case for any of them.

## Two generators per piece

`pseudo_legal_moves` and `attacked_squares` differ for real reasons: a pawn moves
forward and attacks diagonally, and a king defends squares it may not legally
enter. Check detection wants the second.

## Immutability

`ChessBoardState.apply(move)` returns a **new** board and is the only thing that
produces board state. `piece.relocated_to(square)` returns a **new** piece.
`ChessEngine.play` returns a **new** game — which is why taking a move back is just
keeping the engine you already had.

## Running the checks

```bash
uv run python -m pytest
CHESS_SLOW_TESTS=1 uv run python -m pytest
uv run ruff check . && uv run mypy
```

The suite is written with stdlib `unittest` classes, which pytest collects
unchanged. `./infra/scripts/test.sh` runs the same suite in a container, and the
pre-push hook runs it before a push that touches this package.

The most valuable test is `tests_python/perft/`, which counts every legal move
sequence to a given depth in four standard positions and compares against published
totals. Between them they cover castling, en passant, promotion, pins and check
evasion. `CHESS_SLOW_TESTS=1` adds the deeper counts.
