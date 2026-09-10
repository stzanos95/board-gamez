/**
 * The keys every table query is cached under.
 *
 * Built here so that no two call sites can spell one differently, and so that
 * invalidating `all` reaches every table query at once.
 */
export const tableQueryKeys = {
  all: ["lobby", "tables"] as const,
  list: () => [...tableQueryKeys.all, "list"] as const,
  detail: (tableId: string) => [...tableQueryKeys.all, "detail", tableId] as const,
};
