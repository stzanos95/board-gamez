import { QueryClientProvider } from "@tanstack/react-query";
import { useMemo, type ReactElement } from "react";

import { App } from "../components/app/App";
import type { UxConfig } from "../config/ux_config";
import { PlayerProvider } from "../identity/player_context";
import { TableGateway } from "../lobby/table_gateway";
import { AppThemeProvider } from "../theme/AppThemeProvider";
import { GatewayClient } from "../transport/gateway_client";
import { buildQueryClient } from "../transport/query_client";
import { AppServicesProvider, type AppServices } from "./app_services";

export type AppRootProps = {
  readonly config: UxConfig;
};

/**
 * Everything the application needs, built once from the configuration.
 *
 * This is the only place a client, a cache or a theme is constructed. Nothing
 * below it reads a setting.
 */
export function AppRoot(props: AppRootProps): ReactElement {
  const { config } = props;

  const services = useMemo<AppServices>(
    () => ({
      tableGateway: new TableGateway(new GatewayClient(config.gateway)),
      freshness: config.freshness,
    }),
    [config.gateway, config.freshness],
  );

  const queryClient = useMemo(() => buildQueryClient(config.freshness), [config.freshness]);

  return (
    <AppThemeProvider themeName={config.theme}>
      <QueryClientProvider client={queryClient}>
        <AppServicesProvider services={services}>
          <PlayerProvider>
            <App />
          </PlayerProvider>
        </AppServicesProvider>
      </QueryClientProvider>
    </AppThemeProvider>
  );
}
