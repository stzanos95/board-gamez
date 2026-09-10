import type { Table } from "@board-gamez/idl/lobby/model/table_pb";
import { useMutation, useQueryClient, type QueryClient } from "@tanstack/react-query";
import { useCallback, useMemo } from "react";

import { usePlayer } from "../identity/player_context";
import { useTableGateway } from "../runtime/app_services";
import { seatWriteProblem } from "./seat_write_problem";
import { writeSeatChange, type SeatWrite } from "./seat_writer";
import { tableQueryKeys } from "./table_queries";
import { withPlayerRemoved, withPlayerSeated, withPlayerSeatedAnywhere } from "./table_intents";

export type TakeSeatInput = {
  readonly tableId: string;
  readonly seatNumber: number;
};

/**
 * A seat change in progress.
 *
 * `problem` covers both a refusal the lobby made and a call that never
 * arrived, because a player has the same thing to do about either.
 */
export type SeatAction<Input> = {
  readonly run: (input: Input) => void;
  readonly isPending: boolean;
  readonly pendingInput: Input | null;
  readonly problem: string | null;
  readonly dismissProblem: () => void;
};

export function useTakeSeat(): SeatAction<TakeSeatInput> {
  const gateway = useTableGateway();
  const queryClient = useQueryClient();
  const { player } = usePlayer();

  const takeSeat = useCallback(
    (input: TakeSeatInput) =>
      writeSeatChange(gateway, input.tableId, (table: Table) =>
        withPlayerSeated(table, player.id, input.seatNumber),
      ),
    [gateway, player.id],
  );

  const mutation = useMutation({
    mutationFn: takeSeat,
    onSuccess: (write: SeatWrite) => adoptSeatWrite(queryClient, write),
  });

  return useSeatAction({
    run: mutation.mutate,
    isPending: mutation.isPending,
    input: mutation.variables,
    write: mutation.data,
    error: mutation.error,
    dismissProblem: mutation.reset,
  });
}

/**
 * Take whichever seat is open, chosen against the table as it stands when the
 * write is built.
 */
export function useTakeAnySeat(): SeatAction<string> {
  const gateway = useTableGateway();
  const queryClient = useQueryClient();
  const { player } = usePlayer();

  const takeAnySeat = useCallback(
    (tableId: string) =>
      writeSeatChange(gateway, tableId, (table: Table) =>
        withPlayerSeatedAnywhere(table, player.id),
      ),
    [gateway, player.id],
  );

  const mutation = useMutation({
    mutationFn: takeAnySeat,
    onSuccess: (write: SeatWrite) => adoptSeatWrite(queryClient, write),
  });

  return useSeatAction({
    run: mutation.mutate,
    isPending: mutation.isPending,
    input: mutation.variables,
    write: mutation.data,
    error: mutation.error,
    dismissProblem: mutation.reset,
  });
}

export function useLeaveSeat(): SeatAction<string> {
  const gateway = useTableGateway();
  const queryClient = useQueryClient();
  const { player } = usePlayer();

  const leaveSeat = useCallback(
    (tableId: string) =>
      writeSeatChange(gateway, tableId, (table: Table) => withPlayerRemoved(table, player.id)),
    [gateway, player.id],
  );

  const mutation = useMutation({
    mutationFn: leaveSeat,
    onSuccess: (write: SeatWrite) => adoptSeatWrite(queryClient, write),
  });

  return useSeatAction({
    run: mutation.mutate,
    isPending: mutation.isPending,
    input: mutation.variables,
    write: mutation.data,
    error: mutation.error,
    dismissProblem: mutation.reset,
  });
}

/**
 * Put the table the store answered with straight into the cache.
 *
 * The write already carries the stored table, so re-reading it would be a round
 * trip for a value in hand. Both the table and its row in the list are corrected
 * from it: which screen a player belongs on is read off that list, and a stale
 * row would send them back to the table they just left. The refetch that follows
 * is for everyone else's changes.
 */
function adoptSeatWrite(queryClient: QueryClient, write: SeatWrite): void {
  if (write.kind !== "written") {
    return;
  }
  const stored = write.table;
  queryClient.setQueryData(tableQueryKeys.detail(stored.id), stored);
  queryClient.setQueryData(
    tableQueryKeys.list(),
    (cached: readonly Table[] | undefined) =>
      cached?.map((table: Table) => (table.id === stored.id ? stored : table)),
  );
  void queryClient.invalidateQueries({ queryKey: tableQueryKeys.list() });
}

/**
 * The parts of a mutation a seat action is built from.
 */
type SeatMutation<Input> = {
  readonly run: (input: Input) => void;
  readonly isPending: boolean;
  readonly input: Input | undefined;
  readonly write: SeatWrite | undefined;
  readonly error: Error | null;
  readonly dismissProblem: () => void;
};

function useSeatAction<Input>(mutation: SeatMutation<Input>): SeatAction<Input> {
  const { run, isPending, input, write, error, dismissProblem } = mutation;

  const problem = useMemo(() => {
    if (error !== null) {
      return error.message;
    }
    return write === undefined ? null : seatWriteProblem(write);
  }, [error, write]);

  return {
    run,
    isPending,
    pendingInput: isPending && input !== undefined ? input : null,
    problem,
    dismissProblem,
  };
}
