import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useCallback } from "react";

import { useTableGateway } from "../runtime/app_services";
import type { TableGateway } from "./table_gateway";
import { tableQueryKeys } from "./table_queries";

const MISSING_MESSAGE = "That table is no longer there.";

export type DeleteTableAction = {
  readonly run: (tableId: string, onDeleted: () => void) => void;
  readonly isPending: boolean;
  readonly problem: string | null;
  readonly deletedTableId: string | null;
};

/**
 * Retire a table.
 *
 * The version a delete is guarded by is read here rather than carried down
 * from a view, so nothing above this holds a version it has to keep current.
 */
export function useDeleteTable(): DeleteTableAction {
  const gateway = useTableGateway();
  const queryClient = useQueryClient();

  const deleteTable = useCallback(
    (tableId: string) => removeAtCurrentVersion(gateway, tableId),
    [gateway],
  );

  const onDeleted = useCallback(
    (tableId: string | null) => {
      if (tableId === null) {
        return;
      }
      queryClient.removeQueries({ queryKey: tableQueryKeys.detail(tableId) });
      void queryClient.invalidateQueries({ queryKey: tableQueryKeys.list() });
    },
    [queryClient],
  );

  const mutation = useMutation({ mutationFn: deleteTable, onSuccess: onDeleted });

  const { mutate } = mutation;
  const run = useCallback(
    (tableId: string, onDeletedTable: () => void) => {
      mutate(tableId, {
        onSuccess: (deleted: string | null) => {
          if (deleted !== null) {
            onDeletedTable();
          }
        },
      });
    },
    [mutate],
  );

  return {
    run,
    isPending: mutation.isPending,
    problem: mutation.error?.message ?? (mutation.data === null ? MISSING_MESSAGE : null),
    deletedTableId: mutation.data ?? null,
  };
}

async function removeAtCurrentVersion(
  gateway: TableGateway,
  tableId: string,
): Promise<string | null> {
  const current = await gateway.read(tableId);
  if (current === null) {
    return null;
  }
  await gateway.remove(tableId, current.version);
  return tableId;
}
