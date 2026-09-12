import { useCallback, useSyncExternalStore } from "react";

import { useSocketClient } from "../runtime/app_services";
import type { SocketTarget } from "./socket_client";

/**
 * Whether the socket for this target is open right now.
 *
 * Read by a query to decide whether to poll: while the socket is open, a
 * change is announced, and asking on a timer buys nothing. `target` must keep
 * its identity between renders, so a caller builds it once per table.
 */
export function useSocketStatus(target: SocketTarget): boolean {
  const client = useSocketClient();

  const subscribe = useCallback(
    (notify: () => void) => client.subscribeToStatus(target, notify),
    [client, target],
  );
  const read = useCallback(() => client.isOpen(target), [client, target]);

  return useSyncExternalStore(subscribe, read, read);
}
