import type { ChessTable } from "@board-gamez/idl/chess/model/table_pb";
import { useQuery } from "@tanstack/react-query";
import { useCallback, useMemo } from "react";

import { usePlayer } from "../identity/player_context";
import { useChessGateway, useFreshness } from "../runtime/app_services";
import { chessQueryKeys } from "./chess_queries";
import { toChessSeatViews, type ChessSeatView } from "./seat_views";
import { useSeatChoices } from "./use_seat_choices";

export type ChessTableView = {
  readonly seats: readonly ChessSeatView[];
  readonly version: bigint | null;
  readonly isLoading: boolean;
  readonly error: Error | null;
};

/**
 * The chess table's seats with their sides, and the seats the viewer may take.
 *
 * Polled on the table interval, the same as the lobby's view of the table,
 * because both change when someone sits down or stands up.
 */
export function useChessTable(tableId: string): ChessTableView {
  const gateway = useChessGateway();
  const freshness = useFreshness();
  const { player } = usePlayer();
  const { choices, error: choicesError } = useSeatChoices(tableId);

  const fetchTable = useCallback(() => gateway.readTable(tableId), [gateway, tableId]);

  const query = useQuery<ChessTable | null>({
    queryKey: chessQueryKeys.table(tableId),
    queryFn: fetchTable,
    refetchInterval: freshness.tableIntervalMs,
    enabled: tableId.length > 0,
  });

  const table = query.data ?? null;

  const seats = useMemo(
    () =>
      table === null
        ? []
        : toChessSeatViews({
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
