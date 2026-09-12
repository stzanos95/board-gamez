import type { Table } from "@board-gamez/idl/lobby/model/table_pb";
import { useQueryClient, type QueryClient } from "@tanstack/react-query";
import { useEffect } from "react";

import { usePlayer } from "../identity/player_context";
import { useSocketClient } from "../runtime/app_services";
import {
  CHANGE_KEYS_BY_GAME_TYPE,
  EVERY_GAME_CHANGE_KEYS,
} from "../runtime/game_change_keys_registry";
import { invalidateOnChange } from "../transport/query_invalidation";
import { tableTarget, type Change } from "../transport/socket_client";
import type { GameChangeKeys } from "./game_change_keys";
import { tableQueryKeys } from "./table_queries";

const CLOSED_VERSION = 0n;

/**
 * The part of a cached session this hook compares.
 */
type Versioned = {
  readonly version: bigint;
};

/**
 * What the hook is told besides the queries it touches.
 *
 * `onClosed` fires when the table has been closed by someone else; the screen
 * showing it decides where the viewer goes.
 */
export type TableChangeHandlers = {
  readonly onClosed: () => void;
};

/**
 * Keep one table, its seats and its game current from the table's socket
 * while the screen that shows them is mounted.
 *
 * A change names a version. The table and everything drawn from it are read
 * again when the cache holds an older version; the game is read again when
 * the cached session is older. A change the cache is already at is a
 * change this viewer made, and costs nothing. Nothing is written into the
 * cache from a change: it carries nothing to write.
 */
export function useTableChanges(tableId: string, handlers: TableChangeHandlers): void {
  const socketClient = useSocketClient();
  const queryClient = useQueryClient();
  const { player } = usePlayer();
  const { onClosed } = handlers;

  useEffect(() => {
    if (tableId.length === 0) {
      return undefined;
    }
    return socketClient.connect(tableTarget(tableId), {
      onChange: (change: Change) =>
        applyTableChange({ queryClient, tableId, playerId: player.id, change, onClosed }),
      onReconnect: () =>
        invalidateTableQueries(
          queryClient,
          tableId,
          player.id,
          gameChangeKeysOf(queryClient.getQueryData<Table | null>(tableQueryKeys.detail(tableId))),
        ),
    });
  }, [socketClient, queryClient, tableId, player.id, onClosed]);
}

type TableChangeContext = {
  readonly queryClient: QueryClient;
  readonly tableId: string;
  readonly playerId: string;
  readonly change: Change;
  readonly onClosed: () => void;
};

function applyTableChange(context: TableChangeContext): void {
  const { queryClient, tableId, playerId, change, onClosed } = context;
  const cached = queryClient.getQueryData<Table | null>(tableQueryKeys.detail(tableId));
  const games = gameChangeKeysOf(cached);
  if (change.kind === "session") {
    if (change.change.sessionId !== tableId) {
      return;
    }
    games.forEach((game: GameChangeKeys) =>
      invalidateSessionIfOlder(queryClient, game, tableId, change.change.version),
    );
    return;
  }
  if (change.change.tableId !== tableId) {
    return;
  }
  if (change.change.version === CLOSED_VERSION) {
    queryClient.removeQueries({ queryKey: tableQueryKeys.detail(tableId) });
    games.forEach((game: GameChangeKeys) => removeGameQueries(queryClient, game, tableId, playerId));
    invalidateOnChange(queryClient, tableQueryKeys.list());
    onClosed();
    return;
  }
  if (cached === undefined || cached === null || cached.version < change.change.version) {
    invalidateTableQueries(queryClient, tableId, playerId, games);
  }
}

/**
 * The games whose queries a change to this table reaches: the one the table
 * is for, or every game while the table has not been read yet.
 */
function gameChangeKeysOf(cached: Table | null | undefined): readonly GameChangeKeys[] {
  if (cached === undefined || cached === null) {
    return EVERY_GAME_CHANGE_KEYS;
  }
  return [CHANGE_KEYS_BY_GAME_TYPE[cached.gameType]];
}

function invalidateSessionIfOlder(
  queryClient: QueryClient,
  game: GameChangeKeys,
  tableId: string,
  version: bigint,
): void {
  const sessionKey = game.sessionKey(tableId);
  if (sessionKey === null) {
    return;
  }
  const cached = queryClient.getQueryData<Versioned | null>(sessionKey);
  if (cached === undefined || cached === null || cached.version < version) {
    invalidateOnChange(queryClient, sessionKey);
  }
}

function removeGameQueries(
  queryClient: QueryClient,
  game: GameChangeKeys,
  tableId: string,
  playerId: string,
): void {
  const sessionKey = game.sessionKey(tableId);
  if (sessionKey !== null) {
    queryClient.removeQueries({ queryKey: sessionKey });
  }
  game.tableKeys(tableId, playerId).forEach((queryKey) => queryClient.removeQueries({ queryKey }));
}

/**
 * Everything drawn from the table: the lobby's view of it, and what each game
 * keeps for it.
 */
function invalidateTableQueries(
  queryClient: QueryClient,
  tableId: string,
  playerId: string,
  games: readonly GameChangeKeys[],
): void {
  invalidateOnChange(queryClient, tableQueryKeys.detail(tableId));
  games.forEach((game: GameChangeKeys) => {
    game.tableKeys(tableId, playerId).forEach((queryKey) => invalidateOnChange(queryClient, queryKey));
    const sessionKey = game.sessionKey(tableId);
    if (sessionKey !== null) {
      invalidateOnChange(queryClient, sessionKey);
    }
  });
}
