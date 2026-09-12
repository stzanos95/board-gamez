import type { GameChangeKeys } from "../lobby/game_change_keys";
import { chessQueryKeys } from "./chess_queries";

/**
 * What chess keeps for a table: the session, the chess table, and the seats
 * the viewer may take.
 */
export const CHESS_CHANGE_KEYS: GameChangeKeys = {
  sessionKey: (tableId: string) => chessQueryKeys.session(tableId),
  tableKeys: (tableId: string, playerId: string) => [
    chessQueryKeys.table(tableId),
    chessQueryKeys.seatChoices(tableId, playerId),
  ],
};
