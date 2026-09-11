import type { ChessSeatChoice } from "@board-gamez/idl/chess/model/table_pb";
import { useQuery } from "@tanstack/react-query";
import { useCallback } from "react";

import { usePlayer } from "../identity/player_context";
import { useChessGateway, useFreshness } from "../runtime/app_services";
import { chessQueryKeys } from "./chess_queries";

const NO_CHOICES: readonly ChessSeatChoice[] = [];

export type SeatChoicesView = {
  readonly choices: readonly ChessSeatChoice[];
  readonly error: Error | null;
};

/**
 * The seats this viewer may take at a table, as the game offers them.
 *
 * Empty while the answer is loading, and empty once the viewer is seated or
 * the table is full. Polled on the table interval, because another player
 * sitting down takes a choice away.
 */
export function useSeatChoices(tableId: string): SeatChoicesView {
  const gateway = useChessGateway();
  const freshness = useFreshness();
  const { player } = usePlayer();

  const fetchChoices = useCallback(
    () => gateway.listSeatChoices(tableId, player.id),
    [gateway, tableId, player.id],
  );

  const query = useQuery<readonly ChessSeatChoice[]>({
    queryKey: chessQueryKeys.seatChoices(tableId, player.id),
    queryFn: fetchChoices,
    refetchInterval: freshness.tableIntervalMs,
    enabled: tableId.length > 0,
  });

  return {
    choices: query.data ?? NO_CHOICES,
    error: query.error,
  };
}
