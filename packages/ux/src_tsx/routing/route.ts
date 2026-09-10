/**
 * Which screen is on.
 *
 * The lobby is a table list and a table. The location is the fragment, so a
 * table can be opened in a second tab by its link, which is what makes a
 * second player.
 */
export type Route =
  | { readonly screen: "lobby" }
  | { readonly screen: "table"; readonly tableId: string };

export const LOBBY_ROUTE: Route = { screen: "lobby" };

const TABLE_PREFIX = "#/table/";
const LOBBY_FRAGMENT = "#/";

export function routeOf(fragment: string): Route {
  if (!fragment.startsWith(TABLE_PREFIX)) {
    return LOBBY_ROUTE;
  }
  const tableId = decodeURIComponent(fragment.slice(TABLE_PREFIX.length));
  return tableId.length === 0 ? LOBBY_ROUTE : { screen: "table", tableId };
}

export function fragmentOf(route: Route): string {
  if (route.screen === "lobby") {
    return LOBBY_FRAGMENT;
  }
  return `${TABLE_PREFIX}${encodeURIComponent(route.tableId)}`;
}
