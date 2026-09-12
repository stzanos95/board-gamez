import { GameType } from "@board-gamez/idl/game/model/game_type_pb";

import { CHESS_CHANGE_KEYS } from "../chess/chess_change_keys";
import type { GameChangeKeys } from "../lobby/game_change_keys";

const NO_GAME_CHANGE_KEYS: GameChangeKeys = {
  sessionKey: () => null,
  tableKeys: () => [],
};

/**
 * The queries each game keeps for a table.
 *
 * Keyed by the enum, so a game added to the schema does not compile until it
 * has said what a change should reach.
 */
export const CHANGE_KEYS_BY_GAME_TYPE: Record<GameType, GameChangeKeys> = {
  [GameType.UNSPECIFIED]: NO_GAME_CHANGE_KEYS,
  [GameType.CHESS]: CHESS_CHANGE_KEYS,
};

/**
 * Every game's keys, for a table whose game this browser has not read yet.
 * Invalidating a query nothing holds costs nothing.
 */
export const EVERY_GAME_CHANGE_KEYS: readonly GameChangeKeys[] =
  Object.values(CHANGE_KEYS_BY_GAME_TYPE);
