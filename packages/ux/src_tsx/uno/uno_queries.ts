/**
 * The keys every UNO query is cached under.
 *
 * Built here so that no two call sites can spell one differently.
 */
export const unoQueryKeys = {
  all: ["uno"] as const,
  session: (tableId: string) => [...unoQueryKeys.all, "session", tableId] as const,
  table: (tableId: string) => [...unoQueryKeys.all, "table", tableId] as const,
  seatChoices: (tableId: string, playerId: string) =>
    [...unoQueryKeys.all, "seat_choices", tableId, playerId] as const,
};
