import { isBoardSkinName, type BoardSkinName } from "./board_skin_name";

const SKIN_KEY = "board-gamez.chess.skin";

/**
 * The skin the player at this browser last picked, or null when they have
 * not picked one or the browser will not say.
 *
 * Kept in local storage so it outlives the tab. A value that names no skin
 * this build has is treated as no choice.
 */
export function readBoardSkinPreference(): BoardSkinName | null {
  try {
    const stored = window.localStorage.getItem(SKIN_KEY);
    return stored !== null && isBoardSkinName(stored) ? stored : null;
  } catch {
    return null;
  }
}

export function writeBoardSkinPreference(name: BoardSkinName): void {
  try {
    window.localStorage.setItem(SKIN_KEY, name);
  } catch {
    return;
  }
}
