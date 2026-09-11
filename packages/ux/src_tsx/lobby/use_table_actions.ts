import type { Table } from "@board-gamez/idl/lobby/model/table_pb";
import { useMutation, useQueryClient, type QueryClient } from "@tanstack/react-query";
import { useCallback, useMemo } from "react";

import { usePlayer } from "../identity/player_context";
import { useTableGateway } from "../runtime/app_services";
import { tableWriteProblem } from "./table_write_problem";
import { writeTableChange, type TableWrite } from "./table_writer";
import { tableQueryKeys } from "./table_queries";
import {
  withPlayerJoined,
  withPlayerLeft,
  withPlayerSeated,
  withPlayerStood,
} from "./table_intents";

export type TakeSeatInput = {
  readonly tableId: string;
  readonly seatNumber: number;
};

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
    (tableId: string) =>
      writeTableChange(gateway, tableId, (table: Table) => withPlayerJoined(table, player.id)),
    [gateway, player.id],
  );

  const mutation = useMutation({
    mutationFn: joinTable,
    onSuccess: (write: TableWrite) => adoptTableWrite(queryClient, write),
  });

  return useTableAction({
    run: mutation.mutate,
    isPending: mutation.isPending,
    input: mutation.variables,
    write: mutation.data,
    error: mutation.error,
    dismissProblem: mutation.reset,
  });
}

export function useTakeSeat(): TableAction<TakeSeatInput> {
  const gateway = useTableGateway();
  const queryClient = useQueryClient();
  const { player } = usePlayer();

  const takeSeat = useCallback(
    (input: TakeSeatInput) =>
      writeTableChange(gateway, input.tableId, (table: Table) =>
        withPlayerSeated(table, player.id, input.seatNumber),
      ),
    [gateway, player.id],
  );

  const mutation = useMutation({
    mutationFn: takeSeat,
    onSuccess: (write: TableWrite) => adoptTableWrite(queryClient, write),
  });

  return useTableAction({
    run: mutation.mutate,
    isPending: mutation.isPending,
    input: mutation.variables,
    write: mutation.data,
    error: mutation.error,
    dismissProblem: mutation.reset,
  });
}

/**
 * Give up the seat and stay at the table.
 */
export function useStandUp(): TableAction<string> {
  const gateway = useTableGateway();
  const queryClient = useQueryClient();
  const { player } = usePlayer();

  const standUp = useCallback(
    (tableId: string) =>
      writeTableChange(gateway, tableId, (table: Table) => withPlayerStood(table, player.id)),
    [gateway, player.id],
  );

  const mutation = useMutation({
    mutationFn: standUp,
    onSuccess: (write: TableWrite) => adoptTableWrite(queryClient, write),
  });

  return useTableAction({
    run: mutation.mutate,
    isPending: mutation.isPending,
    input: mutation.variables,
    write: mutation.data,
    error: mutation.error,
    dismissProblem: mutation.reset,
  });
}

/**
 * Leave the table, giving up a seat on the way out.
 */
export function useLeaveTable(): TableAction<string> {
  const gateway = useTableGateway();
  const queryClient = useQueryClient();
  const { player } = usePlayer();

  const leaveTable = useCallback(
    (tableId: string) =>
      writeTableChange(gateway, tableId, (table: Table) => withPlayerLeft(table, player.id)),
    [gateway, player.id],
  );

  const mutation = useMutation({
    mutationFn: leaveTable,
    onSuccess: (write: TableWrite) => adoptTableWrite(queryClient, write),
  });

  return useTableAction({
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
function adoptTableWrite(queryClient: QueryClient, write: TableWrite): void {
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
 * The parts of a mutation a table action is built from.
 */
type TableMutation<Input> = {
  readonly run: (input: Input) => void;
  readonly isPending: boolean;
  readonly input: Input | undefined;
  readonly write: TableWrite | undefined;
  readonly error: Error | null;
  readonly dismissProblem: () => void;
};

function useTableAction<Input>(mutation: TableMutation<Input>): TableAction<Input> {
  const { run, isPending, input, write, error, dismissProblem } = mutation;

  const problem = useMemo(() => {
    if (error !== null) {
      return error.message;
    }
    return write === undefined ? null : tableWriteProblem(write);
  }, [error, write]);

  return {
    run,
    isPending,
    pendingInput: isPending && input !== undefined ? input : null,
    problem,
    dismissProblem,
  };
}
