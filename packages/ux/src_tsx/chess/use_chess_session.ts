import { Color } from "@board-gamez/idl/chess/model/piece_pb";
import type { ChessSession } from "@board-gamez/idl/chess/model/session_pb";
import { useQuery, type Query } from "@tanstack/react-query";
import { useCallback, useMemo } from "react";

import { usePlayer } from "../identity/player_context";
import { useChessGateway, useFreshness } from "../runtime/app_services";
import { chessQueryKeys } from "./chess_queries";
import { toChessGameView, type ChessGameView } from "./chess_views";

export type ChessSessionView = {
  readonly game: ChessGameView | null;
  readonly isLoading: boolean;
  readonly error: Error | null;
};

type SessionQuery = Query<ChessSession | null, Error, ChessSession | null>;

/**
 * Whether an answer can still change without this viewer acting.
 *
 * Nothing exists yet while the other player may start the game, and the
 * game moves while it is the other side's turn. Only the side to move can
 * act, so once it is this viewer's turn, or once there is a result, the
 * answer holds until this viewer sends something.
 */
function isAwaitingOthers(session: ChessSession | null | undefined): boolean {
  if (session === undefined || session === null) {
    return true;
  }
  const game = session.game;
  if (game?.result !== undefined) {
    return false;
  }
  return session.color === Color.UNSPECIFIED || session.color !== game?.state?.sideToMove;
}

/**
 * The chess game at a table, as this viewer may see it.
 *
 * A null game is a table where no game has started. The query polls on the
 * game interval while someone else can change the answer and stops while
 * the tab is hidden.
 */
export function useChessSession(tableId: string): ChessSessionView {
  const gateway = useChessGateway();
  const freshness = useFreshness();
  const { player } = usePlayer();

  const fetchSession = useCallback(
    () => gateway.read(tableId, player.id),
    [gateway, tableId, player.id],
  );

  const pollWhileAwaitingOthers = useCallback(
    (query: SessionQuery) =>
      isAwaitingOthers(query.state.data) ? freshness.gameIntervalMs : false,
    [freshness.gameIntervalMs],
  );

  const query = useQuery<ChessSession | null>({
    queryKey: chessQueryKeys.session(tableId),
    queryFn: fetchSession,
    refetchInterval: pollWhileAwaitingOthers,
    enabled: tableId.length > 0,
  });

  const session = query.data ?? null;
  const game = useMemo(() => (session === null ? null : toChessGameView(session)), [session]);

  return {
    game,
    isLoading: query.isPending,
    error: query.error,
  };
}
