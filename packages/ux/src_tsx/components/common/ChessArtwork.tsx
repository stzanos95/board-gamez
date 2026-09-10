import { memo, type ReactElement } from "react";

/**
 * A chess board in its opening position.
 *
 * Drawn rather than fetched: an image file would be a request, a cache policy
 * and a binary in the tree, and this is eight rows of text. The colours come
 * from the theme, so it belongs to whichever one is selected.
 */
const BOARD_SIZE = 8;
const SQUARE = 12;
const BOARD_EXTENT = BOARD_SIZE * SQUARE;
const GLYPH_OFFSET = SQUARE / 2;
const GLYPH_BASELINE_NUDGE = 0.5;

const PIECE_ROWS: readonly string[] = [
  "♜♞♝♛♚♝♞♜",
  "♟♟♟♟♟♟♟♟",
  "",
  "",
  "",
  "",
  "♙♙♙♙♙♙♙♙",
  "♖♘♗♕♔♗♘♖",
];

const DARK_SQUARE_SX = { opacity: 0.55 } as const;

function squares(): readonly ReactElement[] {
  const drawn: ReactElement[] = [];
  for (let rank = 0; rank < BOARD_SIZE; rank += 1) {
    for (let file = 0; file < BOARD_SIZE; file += 1) {
      const isDark = (rank + file) % 2 === 1;
      drawn.push(
        <rect
          key={`${rank}-${file}`}
          x={file * SQUARE}
          y={rank * SQUARE}
          width={SQUARE}
          height={SQUARE}
          fill={isDark ? "currentColor" : "transparent"}
          style={isDark ? DARK_SQUARE_SX : undefined}
        />,
      );
    }
  }
  return drawn;
}

function pieces(): readonly ReactElement[] {
  const drawn: ReactElement[] = [];
  PIECE_ROWS.forEach((row: string, rank: number) => {
    Array.from(row).forEach((glyph: string, file: number) => {
      drawn.push(
        <text
          key={`${rank}-${file}`}
          x={file * SQUARE + GLYPH_OFFSET}
          y={rank * SQUARE + GLYPH_OFFSET + GLYPH_BASELINE_NUDGE}
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize={SQUARE * 0.82}
          fill="currentColor"
        >
          {glyph}
        </text>,
      );
    });
  });
  return drawn;
}

const BOARD_SQUARES = squares();
const BOARD_PIECES = pieces();

export const ChessArtwork = memo(function ChessArtwork(): ReactElement {
  return (
    <svg
      viewBox={`0 0 ${BOARD_EXTENT} ${BOARD_EXTENT}`}
      width="100%"
      role="img"
      aria-label="A chess board in its opening position"
    >
      {BOARD_SQUARES}
      {BOARD_PIECES}
    </svg>
  );
});
