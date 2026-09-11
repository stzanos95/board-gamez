/**
 * The keys every chess query is cached under.
 *
 * Built here so that no two call sites can spell one differently.
 */
export const chessQueryKeys = {
  all: ["chess"] as const,
  session: (tableId: string) => [...chessQueryKeys.all, "session", tableId] as const,
  table: (tableId: string) => [...chessQueryKeys.all, "table", tableId] as const,
  seatChoices: (tableId: string, playerId: string) =>
    [...chessQueryKeys.all, "seat_choices", tableId, playerId] as const,
};
