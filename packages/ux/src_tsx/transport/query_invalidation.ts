import type { QueryClient, QueryKey } from "@tanstack/react-query";

const VISIBLE = "visible";

/**
 * Mark a query stale because a change was announced for it.
 *
 * A screen in front reads again at once. A hidden tab is marked and not
 * asked: it reads when it comes back into view, so a background tab costs
 * nothing for changes it is not showing.
 */
export function invalidateOnChange(queryClient: QueryClient, queryKey: QueryKey): void {
  void queryClient.invalidateQueries({
    queryKey,
    refetchType: document.visibilityState === VISIBLE ? "active" : "none",
  });
}

/**
 * Mark a query stale because this browser wrote something that changes it.
 *
 * A refetch already in flight is left to finish and answers this too: it was
 * started by the frame that announced the write, which reached this browser
 * before the write's own response did. Starting another would read the same
 * value twice.
 */
export function invalidateAfterWrite(queryClient: QueryClient, queryKey: QueryKey): void {
  void queryClient.invalidateQueries({ queryKey }, { cancelRefetch: false });
}
