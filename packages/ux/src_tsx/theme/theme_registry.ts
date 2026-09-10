import { DAYLIGHT_TOKENS } from "./daylight_tokens";
import { MIDNIGHT_TOKENS } from "./midnight_tokens";
import { ThemeName } from "./theme_name";
import type { ThemeTokens } from "./theme_tokens";

/**
 * Every theme this application can be brought up under.
 *
 * Keyed by the enum, so adding a member without adding its tokens does not
 * compile.
 */
export const THEME_TOKENS_BY_NAME: Record<ThemeName, ThemeTokens> = {
  [ThemeName.MIDNIGHT]: MIDNIGHT_TOKENS,
  [ThemeName.DAYLIGHT]: DAYLIGHT_TOKENS,
};
