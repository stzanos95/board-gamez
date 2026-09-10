import Container from "@mui/material/Container";
import { useCallback, type ReactElement } from "react";

import { shortIdentifier } from "../../format/short_identifier";
import { AppHeader } from "./AppHeader";
import { usePlayer } from "../../identity/player_context";
import { LOBBY_ROUTE } from "../../routing/route";
import { useRoute } from "../../routing/use_route";
import { LobbyScreen } from "../lobby/LobbyScreen";
import { TableScreen } from "../table/TableScreen";

const CONTAINER_SX = { pb: 6 } as const;

/**
 * The screen the location names, inside the shell every screen shares.
 */
export function App(): ReactElement {
  const { route, goTo } = useRoute();
  const { player, rename } = usePlayer();

  const handleEnterTable = useCallback(
    (tableId: string) => goTo({ screen: "table", tableId }),
    [goTo],
  );
  const handleLeft = useCallback(() => goTo(LOBBY_ROUTE), [goTo]);

  const screen =
    route.screen === "lobby" ? (
      <LobbyScreen onEnterTable={handleEnterTable} />
    ) : (
      <TableScreen tableId={route.tableId} onLeft={handleLeft} />
    );

  return (
    <Container maxWidth="lg" sx={CONTAINER_SX}>
      <AppHeader
        displayName={player.displayName}
        shortId={shortIdentifier(player.id)}
        onRename={rename}
      />
      {screen}
    </Container>
  );
}
