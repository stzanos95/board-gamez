import type { UnoSession } from "@board-gamez/idl/uno/model/session_pb";
import { useQuery, type Query } from "@tanstack/react-query";
import { useCallback, useMemo } from "react";

import { usePlayer } from "../identity/player_context";
import { useUnoGateway, useFreshness } from "../runtime/app_services";
import { tableTarget } from "../transport/socket_client";
import { useSocketStatus } from "../transport/use_socket_status";
import { unoQueryKeys } from "./uno_queries";
import { toUnoGameView, type UnoGameView } from "./uno_views";

export type UnoSessionView = {
  readonly game: UnoGameView | null;
  readonly isLoading: boolean;
  readonly error: Error | null;
};

type SessionQuery = Query<UnoSession | null, Error, UnoSession | null>;

const NOT_PLAYING = 0;

/**
 * Whether an answer can still change without this viewer acting.
 *
 * Nothing exists yet while another player may start the game, and the game
 * moves while it is someone else's turn. Only the participant to act can
 * act, so once it is this viewer's turn, or once there is a result, the
 * answer holds until this viewer sends something.
 */
function isAwaitingOthers(session: UnoSession | null | undefined): boolean {
  if (session === undefined || session === null) {
    return true;
  }
  const view = session.view;
  if (view?.result !== undefined) {
    return false;
  }
  return session.participant === NOT_PLAYING || session.participant !== view?.participantToAct;
}

/**
 * The UNO game at a table, as this viewer may see it.
 *
 * A null game is a table where no game has started. Changes arrive over the
 * table's socket. Polled only while that socket is not open, on the game
 * interval, while someone else can change the answer, and never while the
 * tab is hidden.
 */
export function useUnoSession(tableId: string): UnoSessionView {
  const gateway = useUnoGateway();
  const freshness = useFreshness();
  const { player } = usePlayer();
  const target = useMemo(() => tableTarget(tableId), [tableId]);
  const isLive = useSocketStatus(target);

  const fetchSession = useCallback(
    () => gateway.read(tableId, player.id),
    [gateway, tableId, player.id],
  );

  const pollWhileAwaitingOthers = useCallback(
    (query: SessionQuery) =>
      !isLive && isAwaitingOthers(query.state.data) ? freshness.gameIntervalMs : false,
    [isLive, freshness.gameIntervalMs],
  );

  const query = useQuery<UnoSession | null>({
    queryKey: unoQueryKeys.session(tableId),
    queryFn: fetchSession,
    refetchInterval: pollWhileAwaitingOthers,
    enabled: tableId.length > 0,
  });

  const session = query.data ?? null;
  const game = useMemo(() => (session === null ? null : toUnoGameView(session)), [session]);

  return {
    game,
    isLoading: query.isPending,
    error: query.error,
  };
}
