import { useMemo } from "react";

import { toSquareViews, type ChessGameView, type SquareKey, type SquareView } from "./chess_views";

const NO_SQUARES: readonly SquareView[] = [];

/**
 * The sixty-four squares of a game, marked for the square the viewer has
 * picked up, and none while no game has begun.
 *
 * Rebuilt only when the game or the selection changes.
 */
export function useBoardSquares(
  game: ChessGameView | null,
  selectedKey: SquareKey | null,
): readonly SquareView[] {
  return useMemo(
    () => (game === null ? NO_SQUARES : toSquareViews(game, selectedKey)),
    [game, selectedKey],
  );
}
