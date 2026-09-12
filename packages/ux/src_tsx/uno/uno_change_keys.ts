import type { GameChangeKeys } from "../lobby/game_change_keys";
import { unoQueryKeys } from "./uno_queries";

/**
 * What UNO keeps for a table: the session, the UNO table, and the seats the
 * viewer may take.
 */
export const UNO_CHANGE_KEYS: GameChangeKeys = {
  sessionKey: (tableId: string) => unoQueryKeys.session(tableId),
  tableKeys: (tableId: string, playerId: string) => [
    unoQueryKeys.table(tableId),
    unoQueryKeys.seatChoices(tableId, playerId),
  ],
};
