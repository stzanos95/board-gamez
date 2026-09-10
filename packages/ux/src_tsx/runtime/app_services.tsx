import { createContext, useContext, type ReactElement, type ReactNode } from "react";

import type { FreshnessSettings } from "../config/ux_config";
import type { TableGateway } from "../lobby/table_gateway";

/**
 * The collaborators every screen reaches for, built once at bringup.
 *
 * Nothing below this constructs a client or reads a setting. A component asks
 * for what it uses and receives that and nothing else.
 */
export type AppServices = {
  readonly tableGateway: TableGateway;
  readonly freshness: FreshnessSettings;
};

const AppServicesContext = createContext<AppServices | null>(null);

export type AppServicesProviderProps = {
  readonly services: AppServices;
  readonly children: ReactNode;
};

export function AppServicesProvider(props: AppServicesProviderProps): ReactElement {
  const { services, children } = props;
  return <AppServicesContext.Provider value={services}>{children}</AppServicesContext.Provider>;
}

function useAppServices(): AppServices {
  const services = useContext(AppServicesContext);
  if (services === null) {
    throw new Error("a screen reached for the application services outside AppServicesProvider");
  }
  return services;
}

export function useTableGateway(): TableGateway {
  return useAppServices().tableGateway;
}

export function useFreshness(): FreshnessSettings {
  return useAppServices().freshness;
}
