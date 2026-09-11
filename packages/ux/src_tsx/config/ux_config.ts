import {
  isBoardSkinName,
  type BoardSkinName,
} from "../components/chess/skins/board_skin_name";
import { isThemeName, type ThemeName } from "../theme/theme_name";

/**
 * Where the gateway answers, and how long a call to it may take.
 *
 * `baseUrl` is prefixed to the path a service declares, so it names the mount
 * point rather than any one operation.
 */
export type GatewaySettings = {
  readonly baseUrl: string;
  readonly requestTimeoutMs: number;
};

/**
 * How current the screens are kept.
 *
 * `staleTimeMs` is how long an answer is reused without asking again, which is
 * what stops a remount from being a request. The intervals are polling, and
 * none of them runs while the tab is hidden.
 */
export type FreshnessSettings = {
  readonly staleTimeMs: number;
  readonly lobbyIntervalMs: number;
  readonly tableIntervalMs: number;
  readonly gameIntervalMs: number;
};

/**
 * How a chess board is drawn until the player at this browser picks a skin.
 */
export type ChessSettings = {
  readonly defaultSkin: BoardSkinName;
};

export type UxConfig = {
  readonly gateway: GatewaySettings;
  readonly theme: ThemeName;
  readonly freshness: FreshnessSettings;
  readonly chess: ChessSettings;
};

const CONFIG_SOURCE = "gamez_ux.json";

function fail(field: string, problem: string): never {
  throw new Error(`${CONFIG_SOURCE}: ${field} ${problem}`);
}

function readObject(source: Record<string, unknown>, field: string): Record<string, unknown> {
  const value = source[field];
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    return fail(field, "must be an object");
  }
  return value as Record<string, unknown>;
}

function readNonEmptyString(source: Record<string, unknown>, field: string): string {
  const value = source[field];
  if (typeof value !== "string" || value.length === 0) {
    return fail(field, "must be a non-empty string");
  }
  return value;
}

function readPositiveInteger(source: Record<string, unknown>, field: string): number {
  const value = source[field];
  if (typeof value !== "number" || !Number.isInteger(value) || value <= 0) {
    return fail(field, "must be a positive whole number");
  }
  return value;
}

/**
 * The settings this application runs under, read from the document the
 * deployable serves.
 *
 * A field that is missing, of the wrong type, or naming a theme that does not
 * exist stops bringup. Nothing here falls back to a default: a misspelled
 * setting that silently works is a fault that only appears in a deployment.
 */
export function parseUxConfig(document: unknown): UxConfig {
  if (typeof document !== "object" || document === null || Array.isArray(document)) {
    return fail("the document", "must be an object");
  }
  const root = document as Record<string, unknown>;

  const gateway = readObject(root, "gateway");
  const freshness = readObject(root, "freshness");
  const chess = readObject(root, "chess");
  const themeName = readNonEmptyString(root, "theme");
  if (!isThemeName(themeName)) {
    return fail("theme", `names no theme this build has: ${themeName}`);
  }
  const defaultSkin = readNonEmptyString(chess, "defaultSkin");
  if (!isBoardSkinName(defaultSkin)) {
    return fail("chess.defaultSkin", `names no board skin this build has: ${defaultSkin}`);
  }

  return {
    gateway: {
      baseUrl: readNonEmptyString(gateway, "baseUrl"),
      requestTimeoutMs: readPositiveInteger(gateway, "requestTimeoutMs"),
    },
    theme: themeName,
    freshness: {
      staleTimeMs: readPositiveInteger(freshness, "staleTimeMs"),
      lobbyIntervalMs: readPositiveInteger(freshness, "lobbyIntervalMs"),
      tableIntervalMs: readPositiveInteger(freshness, "tableIntervalMs"),
      gameIntervalMs: readPositiveInteger(freshness, "gameIntervalMs"),
    },
    chess: { defaultSkin },
  };
}

/**
 * Fetch the configuration document and parse it.
 *
 * Called once, before anything renders.
 */
export async function loadUxConfig(url: string): Promise<UxConfig> {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`${CONFIG_SOURCE}: ${url} answered ${response.status}`);
  }
  return parseUxConfig(await response.json());
}
