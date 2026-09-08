# chess-game

A chess engine. Full rules, no interface: it reads positions and answers questions
about them. Zero dependencies, and no `print` or `input` anywhere in the package.

The import name is `chess`. It ships a `py.typed` marker, so consumers type-check
against it properly.

## Layering

```
core → models → contracts → movement → pieces → board → rules → notation → engine
```

- **`core`** depends on nothing: board dimensions and the error hierarchy.
- **`models`** is the domain vocabulary — every enum and every frozen dataclass,
  one per file. Pure data: a model never imports a board or a rule.
- **`contracts`** is `BoardStateView`, the read-only face a piece is handed.
- Everything above is behaviour.

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
PYTHONPATH=src_python python3 -m unittest discover -s tests_python -t .
CHESS_SLOW_TESTS=1 PYTHONPATH=src_python python3 -m unittest discover -s tests_python -t .
uv run ruff check . && uv run mypy
```

The suite is stdlib `unittest`, so it runs with nothing installed; pytest collects
the same classes unchanged inside the container.

The most valuable test is `tests_python/perft/`, which counts every legal move
sequence to a given depth in four standard positions and compares against published
totals. Between them they cover castling, en passant, promotion, pins and check
evasion. `CHESS_SLOW_TESTS=1` adds the deeper counts.
