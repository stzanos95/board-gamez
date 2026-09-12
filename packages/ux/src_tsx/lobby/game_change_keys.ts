import type { QueryKey } from "@tanstack/react-query";

/**
 * The queries a game keeps for a table, so that a change to the table or to
 * the game at it reaches them without the lobby naming any one game.
 *
 * `sessionKey` names the query holding the game as this viewer sees it; what
 * it holds carries a `version`, which is compared with the version a change
 * announces. Null when the game keeps none. `tableKeys` names every query
 * the game draws from the table besides the lobby's own: its view of the
 * seats, and the seats this viewer may take.
 */
export type GameChangeKeys = {
  readonly sessionKey: (tableId: string) => QueryKey | null;
  readonly tableKeys: (tableId: string, playerId: string) => readonly QueryKey[];
};
