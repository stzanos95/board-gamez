import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useMemo } from "react";

import { usePlayer } from "../identity/player_context";
import { useFreshness, useTableGateway } from "../runtime/app_services";
import { LOBBY_TARGET } from "../transport/socket_client";
import { useSocketStatus } from "../transport/use_socket_status";
import { tableQueryKeys } from "./table_queries";
import { toTableSummaryView, type TableSummaryView } from "./table_views";

export type TablesView = {
  readonly summaries: readonly TableSummaryView[];
  /**
   * The table this player is at, seated or not, or null when they are at none.
   * A player at a table belongs in the table view, not in the list.
   */
  readonly joinedTableId: string | null;
  readonly isLoading: boolean;
  readonly isRefreshing: boolean;
  readonly error: Error | null;
  readonly refresh: () => void;
};

/**
 * Every table in the lobby, in the shape the list draws.
 *
 * Changes arrive over the lobby's socket. Polled only while that socket is
 * not open, and only while the tab is in front. A hidden tab issues nothing.
 */
export function useTables(): TablesView {
  const gateway = useTableGateway();
  const freshness = useFreshness();
  const { player } = usePlayer();
  const queryClient = useQueryClient();
  const isLive = useSocketStatus(LOBBY_TARGET);

  const fetchTables = useCallback(() => gateway.list(), [gateway]);

  const query = useQuery({
    queryKey: tableQueryKeys.list(),
    queryFn: fetchTables,
    refetchInterval: isLive ? false : freshness.lobbyIntervalMs,
  });

  const tables = query.data;
  const summaries = useMemo(
    () => (tables ?? []).map((table) => toTableSummaryView(table, player.id)),
    [tables, player.id],
  );

  const joinedTableId = useMemo(
    () => summaries.find((summary: TableSummaryView) => summary.isAtTable)?.id ?? null,
    [summaries],
  );

  const refresh = useCallback(() => {
    void queryClient.invalidateQueries({ queryKey: tableQueryKeys.list() });
  }, [queryClient]);

  return {
    summaries,
    joinedTableId,
    isLoading: query.isPending,
    isRefreshing: query.isFetching && !query.isPending,
    error: query.error,
    refresh,
  };
}
