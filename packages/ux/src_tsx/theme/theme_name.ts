/**
 * Which look the application is wearing.
 *
 * Selected once, at bringup, from the configuration file. Every option has an
 * entry in THEME_TOKENS_BY_NAME.
 */
export const ThemeName = {
  MIDNIGHT: "midnight",
  DAYLIGHT: "daylight",
} as const;

export type ThemeName = (typeof ThemeName)[keyof typeof ThemeName];

export const THEME_NAMES: readonly ThemeName[] = Object.values(ThemeName);

export function isThemeName(candidate: string): candidate is ThemeName {
  return (THEME_NAMES as readonly string[]).includes(candidate);
}
