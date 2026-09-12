import type { ChessSeatChoice, ChessSeatResult } from "@board-gamez/idl/chess/model/table_pb";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useCallback, useMemo } from "react";

import { usePlayer } from "../identity/player_context";
import { SEAT_OUTCOME_PROBLEMS } from "../lobby/seat_labels";
import { tableQueryKeys } from "../lobby/table_queries";
import { useChessGateway } from "../runtime/app_services";
import { invalidateAfterWrite } from "../transport/query_invalidation";
import { chessQueryKeys } from "./chess_queries";

const GONE_MESSAGE = "That table is no longer there.";

export type TakeSeatInput = {
  readonly tableId: string;
  readonly choice: ChessSeatChoice;
  readonly expectedVersion: bigint;
};

export type TakeSeatAction = {
  readonly run: (input: TakeSeatInput) => void;
  readonly isPending: boolean;
  readonly pendingChoice: ChessSeatChoice | null;
  readonly problem: string | null;
};

/**
 * Take a seat at the chess table, as one of the choices the game offered.
 *
 * The result carries the table as it now stands, which goes straight into the
 * cache whatever the outcome. The lobby's view of the same table and the
 * choices on offer are re-read, because both changed with it.
 */
export function useTakeSeat(): TakeSeatAction {
  const gateway = useChessGateway();
  const queryClient = useQueryClient();
  const { player } = usePlayer();

  const takeSeat = useCallback(
    (input: TakeSeatInput) =>
      gateway.takeSeat({
        tableId: input.tableId,
        playerId: player.id,
        choice: input.choice,
        expectedVersion: input.expectedVersion,
      }),
    [gateway, player.id],
  );

  const onAnswered = useCallback(
    (result: ChessSeatResult | null, input: TakeSeatInput) => {
      if (result?.table !== undefined) {
        queryClient.setQueryData(chessQueryKeys.table(input.tableId), result.table);
      }
      invalidateAfterWrite(queryClient, tableQueryKeys.detail(input.tableId));
      invalidateAfterWrite(queryClient, tableQueryKeys.list());
      invalidateAfterWrite(queryClient, chessQueryKeys.seatChoices(input.tableId, player.id));
    },
    [queryClient, player.id],
  );

  const mutation = useMutation({ mutationFn: takeSeat, onSuccess: onAnswered });

  const problem = useMemo(() => {
    if (mutation.error !== null) {
      return mutation.error.message;
    }
    if (mutation.data === undefined) {
      return null;
    }
    return mutation.data === null ? GONE_MESSAGE : SEAT_OUTCOME_PROBLEMS[mutation.data.outcome];
  }, [mutation.error, mutation.data]);

  return {
    run: mutation.mutate,
    isPending: mutation.isPending,
    pendingChoice: mutation.isPending ? (mutation.variables?.choice ?? null) : null,
    problem,
  };
}
