import type { BoardSkin } from "./board_skin";
import { BoardSkinName } from "./board_skin_name";
import { CARTOON_SKIN } from "./cartoon_skin";
import { CLASSIC_SKIN } from "./classic_skin";
import { WOODEN_SKIN } from "./wooden_skin";

/**
 * Every skin a chess board can be drawn in.
 *
 * Keyed by the enum, so adding a member without adding its skin does not
 * compile.
 */
export const BOARD_SKINS_BY_NAME: Record<BoardSkinName, BoardSkin> = {
  [BoardSkinName.CLASSIC]: CLASSIC_SKIN,
  [BoardSkinName.WOODEN]: WOODEN_SKIN,
  [BoardSkinName.CARTOON]: CARTOON_SKIN,
};
