import { useCallback, useMemo, useSyncExternalStore } from "react";

import { fragmentOf, routeOf, type Route } from "./route";

const HASH_CHANGE = "hashchange";

export type Navigation = {
  readonly route: Route;
  readonly goTo: (route: Route) => void;
};

function subscribeToFragment(notify: () => void): () => void {
  window.addEventListener(HASH_CHANGE, notify);
  return () => window.removeEventListener(HASH_CHANGE, notify);
}

function readFragment(): string {
  return window.location.hash;
}

/**
 * The screen the location names, and the one way to change it.
 *
 * Reads the fragment through the browser's own event rather than a timer, so
 * nothing polls the address bar.
 */
export function useRoute(): Navigation {
  const fragment = useSyncExternalStore(subscribeToFragment, readFragment, readFragment);
  const route = useMemo(() => routeOf(fragment), [fragment]);

  const goTo = useCallback((next: Route) => {
    window.location.hash = fragmentOf(next);
  }, []);

  return { route, goTo };
}
