import type { Table } from "@board-gamez/idl/lobby/model/table_pb";
import { useQueryClient, type QueryClient } from "@tanstack/react-query";
import { useEffect } from "react";

import { useSocketClient } from "../runtime/app_services";
import { invalidateOnChange } from "../transport/query_invalidation";
import { LOBBY_TARGET, type Change } from "../transport/socket_client";
import { tableQueryKeys } from "./table_queries";

const CLOSED_VERSION = 0n;

/**
 * Keep the list of tables current from the lobby's socket while the screen
 * that shows it is mounted.
 *
 * A change names a table and its version. The list is read again when it
 * holds an older version of that table, does not hold it, or holds one that
 * has been closed. Nothing is written into the cache from a change: it
 * carries nothing to write.
 */
export function useLobbyChanges(): void {
  const socketClient = useSocketClient();
  const queryClient = useQueryClient();

  useEffect(
    () =>
      socketClient.connect(LOBBY_TARGET, {
        onChange: (change: Change) => applyLobbyChange(queryClient, change),
        onReconnect: () => invalidateOnChange(queryClient, tableQueryKeys.list()),
      }),
    [socketClient, queryClient],
  );
}

function applyLobbyChange(queryClient: QueryClient, change: Change): void {
  if (change.kind !== "table") {
    return;
  }
  const { tableId, version } = change.change;
  const cached = queryClient.getQueryData<readonly Table[]>(tableQueryKeys.list());
  const row = cached?.find((table: Table) => table.id === tableId);
  if (version === CLOSED_VERSION) {
    if (row !== undefined) {
      invalidateOnChange(queryClient, tableQueryKeys.list());
    }
    return;
  }
  if (row === undefined || row.version < version) {
    invalidateOnChange(queryClient, tableQueryKeys.list());
  }
}
