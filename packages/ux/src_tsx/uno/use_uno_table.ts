import type { UnoTable } from "@board-gamez/idl/uno/model/table_pb";
import { useQuery } from "@tanstack/react-query";
import { useCallback, useMemo } from "react";

import { usePlayer } from "../identity/player_context";
import { useUnoGateway, useFreshness } from "../runtime/app_services";
import { tableTarget } from "../transport/socket_client";
import { useSocketStatus } from "../transport/use_socket_status";
import { unoQueryKeys } from "./uno_queries";
import { toUnoSeatViews, type UnoSeatView } from "./seat_views";
import { useSeatChoices } from "./use_seat_choices";

export type UnoTableView = {
  readonly seats: readonly UnoSeatView[];
  readonly version: bigint | null;
  readonly isLoading: boolean;
  readonly error: Error | null;
};

/**
 * The UNO table's seats, and the seats the viewer may take.
 *
 * Changes arrive over the table's socket. Polled only while that socket is
 * not open, on the table interval, the same as the lobby's view of the table,
 * because both change when someone sits down or stands up.
 */
export function useUnoTable(tableId: string): UnoTableView {
  const gateway = useUnoGateway();
  const freshness = useFreshness();
  const { player } = usePlayer();
  const { choices, error: choicesError } = useSeatChoices(tableId);
  const target = useMemo(() => tableTarget(tableId), [tableId]);
  const isLive = useSocketStatus(target);

  const fetchTable = useCallback(() => gateway.readTable(tableId), [gateway, tableId]);

  const query = useQuery<UnoTable | null>({
    queryKey: unoQueryKeys.table(tableId),
    queryFn: fetchTable,
    refetchInterval: isLive ? false : freshness.tableIntervalMs,
    enabled: tableId.length > 0,
  });

  const table = query.data ?? null;

  const seats = useMemo(
    () =>
      table === null
        ? []
        : toUnoSeatViews({
            table,
            choices,
            viewerId: player.id,
            viewerName: player.displayName,
          }),
    [table, choices, player.id, player.displayName],
  );

  return {
    seats,
    version: table?.version ?? null,
    isLoading: query.isPending,
    error: query.error ?? choicesError,
  };
}
