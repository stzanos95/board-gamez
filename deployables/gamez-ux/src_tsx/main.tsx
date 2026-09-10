/**
 * Entry point for the browser.
 *
 * Reads the settings document the deployable serves, then mounts the
 * application with it. Nothing is rendered before the settings are in hand: a
 * screen brought up on defaults would hide a misconfigured deployment until a
 * request failed.
 */
import { loadUxConfig } from "@board-gamez/ux/config/ux_config";
import { AppRoot } from "@board-gamez/ux/runtime/AppRoot";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

const CONFIG_URL = "/gamez_ux.json";
const ROOT_ELEMENT_ID = "root";

async function main(): Promise<void> {
  const container = document.getElementById(ROOT_ELEMENT_ID);
  if (container === null) {
    throw new Error(`index.html has no #${ROOT_ELEMENT_ID} to mount into`);
  }
  const config = await loadUxConfig(CONFIG_URL);
  createRoot(container).render(
    <StrictMode>
      <AppRoot config={config} />
    </StrictMode>,
  );
}

function reportBringupFailure(cause: unknown): void {
  const detail = cause instanceof Error ? cause.message : String(cause);
  document.body.textContent = `board-gamez did not start: ${detail}`;
}

main().catch(reportBringupFailure);
