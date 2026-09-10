import { QueryClient } from "@tanstack/react-query";

import type { FreshnessSettings } from "../config/ux_config";
import { isWorthRetrying } from "./gateway_error";

/**
 * How long an answer nothing is watching is kept before it is dropped.
 *
 * Held down deliberately: the cache is the application's largest allocation,
 * and a player who has moved on from a table does not need it back.
 */
const CACHE_RETENTION_MS = 120_000;

const MAXIMUM_ATTEMPTS = 2;

/**
 * The cache every screen reads through.
 *
 * Polling never runs while the tab is hidden, so a lobby left open in a
 * background tab issues no requests and holds no timer.
 */
export function buildQueryClient(freshness: FreshnessSettings): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: freshness.staleTimeMs,
        gcTime: CACHE_RETENTION_MS,
        refetchOnWindowFocus: true,
        refetchOnReconnect: true,
        refetchIntervalInBackground: false,
        retry: (attempt: number, error: unknown) =>
          attempt < MAXIMUM_ATTEMPTS && isWorthRetrying(error),
      },
      mutations: { retry: false },
    },
  });
}
