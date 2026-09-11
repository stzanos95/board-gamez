/**
 * The grid every frame arranges: rank labels down the left, the squares to
 * their right, file labels under the squares.
 */
export const FRAME_GRID_SX = {
  display: "grid",
  gridTemplateColumns: "auto minmax(0, 1fr)",
  gridTemplateRows: "minmax(0, 1fr) auto",
  columnGap: 0.5,
  rowGap: 0.5,
} as const;
