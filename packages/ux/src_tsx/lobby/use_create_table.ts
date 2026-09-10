import type { GameType } from "@board-gamez/idl/lobby/model/game_type_pb";
import type { Table } from "@board-gamez/idl/lobby/model/table_pb";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useCallback } from "react";

import { usePlayer } from "../identity/player_context";
import { useTableGateway } from "../runtime/app_services";
import { tableQueryKeys } from "./table_queries";
import { newTable } from "./table_intents";

const REFUSED_MESSAGE = "The lobby refused the new table. Try again.";

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
 * Open a table, with this player in the first seat.
 *
 * The stored table is written into both caches, so the list is correct before a
 * refetch lands and the host is carried to their table without waiting for one.
 */
export function useCreateTable(): CreateTableAction {
  const gateway = useTableGateway();
  const queryClient = useQueryClient();
  const { player } = usePlayer();

  const createTable = useCallback(
    (input: NewTableInput) =>
      gateway.upsert(newTable(input.gameType, input.seatCount, player.id)),
    [gateway, player.id],
  );

  const onCreated = useCallback(
    (stored: Table | null) => {
      if (stored === null) {
        return;
      }
      queryClient.setQueryData(tableQueryKeys.detail(stored.id), stored);
      queryClient.setQueryData(
        tableQueryKeys.list(),
        (cached: readonly Table[] | undefined) => [...(cached ?? []), stored],
      );
      void queryClient.invalidateQueries({ queryKey: tableQueryKeys.list() });
    },
    [queryClient],
  );

  const mutation = useMutation({ mutationFn: createTable, onSuccess: onCreated });

  return {
    run: mutation.mutate,
    isPending: mutation.isPending,
    problem: mutation.error?.message ?? (mutation.data === null ? REFUSED_MESSAGE : null),
  };
}
