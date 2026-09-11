/**
 * Which look a chess board is wearing.
 *
 * The configuration names the skin a browser starts with, and the player may
 * pick another at any time. Every option has an entry in BOARD_SKINS_BY_NAME.
 */
export const BoardSkinName = {
  CLASSIC: "classic",
  WOODEN: "wooden",
  CARTOON: "cartoon",
} as const;

export type BoardSkinName = (typeof BoardSkinName)[keyof typeof BoardSkinName];

export const BOARD_SKIN_NAMES: readonly BoardSkinName[] = Object.values(BoardSkinName);

export function isBoardSkinName(candidate: string): candidate is BoardSkinName {
  return (BOARD_SKIN_NAMES as readonly string[]).includes(candidate);
}
