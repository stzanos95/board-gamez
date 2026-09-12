import type { GameType } from "@board-gamez/idl/game/model/game_type_pb";
import type { SeatResult } from "@board-gamez/idl/lobby/model/seat_result_pb";
import { SeatOutcome } from "@board-gamez/idl/lobby/model/seat_result_pb";
import type { Table } from "@board-gamez/idl/lobby/model/table_pb";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useCallback, useMemo } from "react";

import { usePlayer } from "../identity/player_context";
import { useTableGateway } from "../runtime/app_services";
import { invalidateAfterWrite } from "../transport/query_invalidation";
import { SEAT_OUTCOME_PROBLEMS } from "./seat_labels";
import { tableQueryKeys } from "./table_queries";

const UNANSWERED_MESSAGE = "The lobby did not answer the new table. Try again.";

export type NewTableInput = {
  readonly gameType: GameType;
  readonly seatCount: number;
};

export type CreateTableAction = {
  readonly run: (input: NewTableInput) => void;
  readonly isPending: boolean;
  readonly problem: string | null;
};

/**
 * Open a table, with this player at it and every seat open.
 *
 * The table the lobby answers is written into both caches, so the list is
 * correct before a refetch lands and the opener is carried to their table
 * without waiting for one.
 */
export function useCreateTable(): CreateTableAction {
  const gateway = useTableGateway();
  const queryClient = useQueryClient();
  const { player } = usePlayer();

  const createTable = useCallback(
    (input: NewTableInput) => gateway.createTable(input.gameType, input.seatCount, player.id),
    [gateway, player.id],
  );

  const onCreated = useCallback(
    (result: SeatResult | null) => {
      if (result?.outcome !== SeatOutcome.CREATED || result.table === undefined) {
        return;
      }
      const stored = result.table;
      queryClient.setQueryData(tableQueryKeys.detail(stored.id), stored);
      queryClient.setQueryData(
        tableQueryKeys.list(),
        (cached: readonly Table[] | undefined) => [...(cached ?? []), stored],
      );
      invalidateAfterWrite(queryClient, tableQueryKeys.list());
    },
    [queryClient],
  );

  const mutation = useMutation({ mutationFn: createTable, onSuccess: onCreated });

  const { error, data: result } = mutation;
  const problem = useMemo(() => {
    if (error !== null) {
      return error.message;
    }
    if (result === undefined) {
      return null;
    }
    return result === null ? UNANSWERED_MESSAGE : SEAT_OUTCOME_PROBLEMS[result.outcome];
  }, [error, result]);

  return {
    run: mutation.mutate,
    isPending: mutation.isPending,
    problem,
  };
}
