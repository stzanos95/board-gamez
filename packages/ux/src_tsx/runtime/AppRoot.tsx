import { QueryClientProvider } from "@tanstack/react-query";
import { useMemo, type ReactElement } from "react";

import { ChessGateway } from "../chess/chess_gateway";
import { App } from "../components/app/App";
import { BoardSkinProvider } from "../components/chess/skins/board_skin_context";
import type { UxConfig } from "../config/ux_config";
import { PlayerProvider } from "../identity/player_context";
import { TableGateway } from "../lobby/table_gateway";
import { AppThemeProvider } from "../theme/AppThemeProvider";
import { GatewayClient } from "../transport/gateway_client";
import { buildQueryClient } from "../transport/query_client";
import { SocketClient } from "../transport/socket_client";
import { AppServicesProvider, type AppServices } from "./app_services";
import { buildPackedTypeRegistry } from "./packed_types";

export type AppRootProps = {
  readonly config: UxConfig;
};

/**
 * Everything the application needs, built once from the configuration.
 *
 * This is the only place a client, a socket, a cache, a theme or a board skin
 * is constructed. Nothing below it reads a setting.
 */
export function AppRoot(props: AppRootProps): ReactElement {
  const { config } = props;

  const services = useMemo<AppServices>(() => {
    const client = new GatewayClient(config.gateway, buildPackedTypeRegistry());
    return {
      tableGateway: new TableGateway(client),
      chessGateway: new ChessGateway(client),
      socketClient: new SocketClient(config.socket),
      freshness: config.freshness,
    };
  }, [config.gateway, config.socket, config.freshness]);

  const queryClient = useMemo(() => buildQueryClient(config.freshness), [config.freshness]);

  return (
    <AppThemeProvider themeName={config.theme}>
      <QueryClientProvider client={queryClient}>
        <AppServicesProvider services={services}>
          <PlayerProvider>
            <BoardSkinProvider defaultSkin={config.chess.defaultSkin}>
              <App />
            </BoardSkinProvider>
          </PlayerProvider>
        </AppServicesProvider>
      </QueryClientProvider>
    </AppThemeProvider>
  );
}
