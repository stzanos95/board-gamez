import type { UnoSession } from "@board-gamez/idl/uno/model/session_pb";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useCallback } from "react";

import { usePlayer } from "../identity/player_context";
import { tableQueryKeys } from "../lobby/table_queries";
import { useUnoGateway } from "../runtime/app_services";
import { invalidateAfterWrite } from "../transport/query_invalidation";
import { unoQueryKeys } from "./uno_queries";

const REFUSED_MESSAGE =
  "The game did not start. Every seat has to be taken, and you have to be in one.";

export type StartGameAction = {
  readonly run: (tableId: string) => void;
  readonly isPending: boolean;
  readonly problem: string | null;
};

/**
 * Begin the UNO game at a table.
 *
 * A game already being played comes back as it stands, so a second start is
 * a read. The session answered goes straight into the cache, and the table
 * is re-read because its seats are now a roster.
 */
export function useStartGame(): StartGameAction {
  const gateway = useUnoGateway();
  const queryClient = useQueryClient();
  const { player } = usePlayer();

  const startGame = useCallback(
    (tableId: string) => gateway.start(tableId, player.id),
    [gateway, player.id],
  );

  const onStarted = useCallback(
    (session: UnoSession | null) => {
      if (session === null) {
        return;
      }
      queryClient.setQueryData(unoQueryKeys.session(session.id), session);
      invalidateAfterWrite(queryClient, tableQueryKeys.detail(session.id));
    },
    [queryClient],
  );

  const mutation = useMutation({ mutationFn: startGame, onSuccess: onStarted });

  return {
    run: mutation.mutate,
    isPending: mutation.isPending,
    problem: mutation.error?.message ?? (mutation.data === null ? REFUSED_MESSAGE : null),
  };
}
