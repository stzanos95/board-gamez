/**
 * The layers every square ground stacks: the ground fills the square, an
 * overlay paints over it, and the piece sits inside a margin.
 */
export const GROUND_SX = {
  position: "absolute",
  inset: 0,
  overflow: "hidden",
} as const;

export const OVERLAY_SX = {
  position: "absolute",
  inset: 0,
  pointerEvents: "none",
} as const;

export const PIECE_SLOT_SX = {
  position: "absolute",
  inset: "7%",
  display: "flex",
} as const;
