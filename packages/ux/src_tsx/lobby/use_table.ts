import type { Table } from "@board-gamez/idl/lobby/model/table_pb";
import { useQuery } from "@tanstack/react-query";
import { useCallback, useMemo } from "react";

import { usePlayer } from "../identity/player_context";
import { useFreshness, useTableGateway } from "../runtime/app_services";
import { tableTarget } from "../transport/socket_client";
import { useSocketStatus } from "../transport/use_socket_status";
import { tableQueryKeys } from "./table_queries";
import { toSeatViews, toTableSummaryView, type SeatView, type TableSummaryView } from "./table_views";

export type TableView = {
  readonly summary: TableSummaryView | null;
  readonly seats: readonly SeatView[];
  readonly isLoading: boolean;
  readonly isMissing: boolean;
  readonly error: Error | null;
};

/**
 * One table and its seats.
 *
 * Changes arrive over the table's socket. Polled only while that socket is
 * not open, more often than the lobby list because this is the screen a
 * player waits on.
 */
export function useTable(tableId: string): TableView {
  const gateway = useTableGateway();
  const freshness = useFreshness();
  const { player } = usePlayer();
  const target = useMemo(() => tableTarget(tableId), [tableId]);
  const isLive = useSocketStatus(target);

  const fetchTable = useCallback(() => gateway.read(tableId), [gateway, tableId]);

  const query = useQuery<Table | null>({
    queryKey: tableQueryKeys.detail(tableId),
    queryFn: fetchTable,
    refetchInterval: isLive ? false : freshness.tableIntervalMs,
    enabled: tableId.length > 0,
  });

  const table = query.data ?? null;

  const summary = useMemo(
    () => (table === null ? null : toTableSummaryView(table, player.id)),
    [table, player.id],
  );

  const seats = useMemo(
    () => (table === null ? [] : toSeatViews(table, player.id, player.displayName)),
    [table, player.id, player.displayName],
  );

  return {
    summary,
    seats,
    isLoading: query.isPending,
    isMissing: !query.isPending && query.error === null && table === null,
    error: query.error,
  };
}
