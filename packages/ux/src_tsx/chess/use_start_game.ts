import type { ChessSession } from "@board-gamez/idl/chess/model/session_pb";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useCallback } from "react";

import { usePlayer } from "../identity/player_context";
import { tableQueryKeys } from "../lobby/table_queries";
import { useChessGateway } from "../runtime/app_services";
import { chessQueryKeys } from "./chess_queries";

const REFUSED_MESSAGE =
  "The game did not start. Every seat has to be taken, and you have to be in one.";

export type StartGameAction = {
  readonly run: (tableId: string) => void;
  readonly isPending: boolean;
  readonly problem: string | null;
};

/**
 * Begin the chess game at a table.
 *
 * A game already being played comes back as it stands, so a second start is
 * a read. The session answered goes straight into the cache, and the table
 * is re-read because its seats are now a roster.
 */
export function useStartGame(): StartGameAction {
  const gateway = useChessGateway();
  const queryClient = useQueryClient();
  const { player } = usePlayer();

  const startGame = useCallback(
    (tableId: string) => gateway.start(tableId, player.id),
    [gateway, player.id],
  );

  const onStarted = useCallback(
    (session: ChessSession | null) => {
      if (session === null) {
        return;
      }
      queryClient.setQueryData(chessQueryKeys.session(session.id), session);
      void queryClient.invalidateQueries({ queryKey: tableQueryKeys.detail(session.id) });
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
