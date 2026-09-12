import type { SeatResult } from "@board-gamez/idl/lobby/model/seat_result_pb";
import type { Table } from "@board-gamez/idl/lobby/model/table_pb";
import { useMutation, useQueryClient, type QueryClient } from "@tanstack/react-query";
import { useCallback, useMemo } from "react";

import { usePlayer } from "../identity/player_context";
import { useTableGateway } from "../runtime/app_services";
import { CHANGE_KEYS_BY_GAME_TYPE } from "../runtime/game_change_keys_registry";
import { invalidateAfterWrite } from "../transport/query_invalidation";
import { SEAT_OUTCOME_PROBLEMS } from "./seat_labels";
import { tableQueryKeys } from "./table_queries";

const GONE_MESSAGE = "That table is no longer there.";

/**
 * A change to a table in progress.
 *
 * `problem` covers both a refusal the lobby made and a call that never
 * arrived, because a player has the same thing to do about either.
 */
export type TableAction<Input> = {
  readonly run: (input: Input) => void;
  readonly isPending: boolean;
  readonly pendingInput: Input | null;
  readonly problem: string | null;
  readonly dismissProblem: () => void;
};

/**
 * Join a table without taking a seat.
 */
export function useJoinTable(): TableAction<string> {
  const gateway = useTableGateway();
  const queryClient = useQueryClient();
  const { player } = usePlayer();

  const joinTable = useCallback(
    (tableId: string) => gateway.joinTable(tableId, player.id),
    [gateway, player.id],
  );

  const mutation = useMutation({
    mutationFn: joinTable,
    onSuccess: (result: SeatResult | null) => adoptSeatResult(queryClient, result, player.id),
  });

  return useSeatAction({
    run: mutation.mutate,
    isPending: mutation.isPending,
    input: mutation.variables,
    result: mutation.data,
    error: mutation.error,
    dismissProblem: mutation.reset,
  });
}

/**
 * Give up the seat and stay at the table.
 *
 * The lobby withdraws a seated player from the game being played before it
 * opens the seat, so the game's own view is re-read along with the table: in
 * chess, standing up is a resignation.
 */
export function useStandUp(): TableAction<string> {
  const gateway = useTableGateway();
  const queryClient = useQueryClient();
  const { player } = usePlayer();

  const standUp = useCallback(
    (tableId: string) => gateway.vacateSeat(tableId, player.id),
    [gateway, player.id],
  );

  const mutation = useMutation({
    mutationFn: standUp,
    onSuccess: (result: SeatResult | null) => adoptSeatResult(queryClient, result, player.id),
  });

  return useSeatAction({
    run: mutation.mutate,
    isPending: mutation.isPending,
    input: mutation.variables,
    result: mutation.data,
    error: mutation.error,
    dismissProblem: mutation.reset,
  });
}

/**
 * Leave the table, giving up a seat on the way out. A seated player is
 * withdrawn from the game being played, as when standing up.
 */
export function useLeaveTable(): TableAction<string> {
  const gateway = useTableGateway();
  const queryClient = useQueryClient();
  const { player } = usePlayer();

  const leaveTable = useCallback(
    (tableId: string) => gateway.leaveTable(tableId, player.id),
    [gateway, player.id],
  );

  const mutation = useMutation({
    mutationFn: leaveTable,
    onSuccess: (result: SeatResult | null) => adoptSeatResult(queryClient, result, player.id),
  });

  return useSeatAction({
    run: mutation.mutate,
    isPending: mutation.isPending,
    input: mutation.variables,
    result: mutation.data,
    error: mutation.error,
    dismissProblem: mutation.reset,
  });
}

/**
 * Put the table a seat change answered with straight into the cache, and
 * re-read what the change may have moved: the lobby's list, and everything
 * the game at that table keeps, which a withdrawal changes.
 *
 * The answer already carries the stored table, so re-reading it would be a
 * round trip for a value in hand. Both the table and its row in the list are
 * corrected from it: which screen a player belongs on is read off that list,
 * and a stale row would send them to the wrong one. The refetch that follows
 * is for everyone else's changes.
 */
function adoptSeatResult(
  queryClient: QueryClient,
  result: SeatResult | null,
  playerId: string,
): void {
  if (result?.table === undefined) {
    invalidateAfterWrite(queryClient, tableQueryKeys.list());
    return;
  }
  const stored = result.table;
  queryClient.setQueryData(tableQueryKeys.detail(stored.id), stored);
  queryClient.setQueryData(
    tableQueryKeys.list(),
    (cached: readonly Table[] | undefined) =>
      cached?.map((table: Table) => (table.id === stored.id ? stored : table)),
  );
  invalidateAfterWrite(queryClient, tableQueryKeys.list());
  const game = CHANGE_KEYS_BY_GAME_TYPE[stored.gameType];
  game.tableKeys(stored.id, playerId).forEach((queryKey) => invalidateAfterWrite(queryClient, queryKey));
  const sessionKey = game.sessionKey(stored.id);
  if (sessionKey !== null) {
    invalidateAfterWrite(queryClient, sessionKey);
  }
}

/**
 * The parts of a mutation a seat change is built from.
 */
type SeatMutation<Input> = {
  readonly run: (input: Input) => void;
  readonly isPending: boolean;
  readonly input: Input | undefined;
  readonly result: SeatResult | null | undefined;
  readonly error: Error | null;
  readonly dismissProblem: () => void;
};

function useSeatAction<Input>(mutation: SeatMutation<Input>): TableAction<Input> {
  const { run, isPending, input, result, error, dismissProblem } = mutation;

  const problem = useMemo(() => {
    if (error !== null) {
      return error.message;
    }
    if (result === undefined) {
      return null;
    }
    return result === null ? GONE_MESSAGE : SEAT_OUTCOME_PROBLEMS[result.outcome];
  }, [error, result]);

  return {
    run,
    isPending,
    pendingInput: isPending && input !== undefined ? input : null,
    problem,
    dismissProblem,
  };
}
